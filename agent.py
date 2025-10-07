"""Langgraph-based conversation agent for metadata extraction using GPT-5."""
from typing import Dict, Any, List, Optional
from openai import OpenAI
from langgraph.graph import StateGraph, END
from schema_loader import SchemaManager, Field
from models import WorkflowState, WorkflowPhase, FieldStatus
from validator import MetadataValidator
import json
import os
import re


class MetadataAgent:
    """Agent for guiding metadata extraction workflow using GPT-5-Mini."""
    
    def __init__(self, api_key: str = None, model: str = None, base_url: str = None, 
                 reasoning_effort: str = None, verbosity: str = None):
        """
        Initialize metadata extraction agent.
        
        Args:
            api_key: OpenAI API key (default: from OPENAI_API_KEY env)
            model: Model name (default: from OPENAI_MODEL env or "gpt-5-mini")
            base_url: OpenAI API base URL (default: from OPENAI_BASE_URL env or None)
            reasoning_effort: GPT-5 reasoning level - only used for gpt-5* models (default: from GPT5_REASONING_EFFORT env or "minimal")
            verbosity: Response verbosity - only used for gpt-5* models (default: from GPT5_VERBOSITY env or "low")
        """
        # Load from environment if not provided
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-5-mini")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        
        # GPT-5 specific parameters (only used if model starts with "gpt-5")
        self.default_reasoning_effort = reasoning_effort or os.getenv("GPT5_REASONING_EFFORT", "minimal")
        self.default_verbosity = verbosity or os.getenv("GPT5_VERBOSITY", "low")
        
        # Check if this is a GPT-5 model
        self.is_gpt5 = self.model.startswith("gpt-5")
        
        # Validate
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not provided. Set it via parameter or environment variable.")
        
        # Initialize OpenAI client
        client_kwargs = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url
        self.client = OpenAI(**client_kwargs)
        
        # Initialize schema manager and validator
        self.schema_manager = SchemaManager()
        self.validator = MetadataValidator()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the Langgraph workflow."""
        workflow = StateGraph(WorkflowState)

        
        # Add nodes
        workflow.add_node("init", self._init_node)
        workflow.add_node("suggest_special_schemas", self._suggest_special_schemas_node)
        workflow.add_node("extract_core_required", self._extract_core_required_node)
        workflow.add_node("extract_core_optional", self._extract_core_optional_node)
        workflow.add_node("extract_special_required", self._extract_special_required_node)
        workflow.add_node("extract_special_optional", self._extract_special_optional_node)
        workflow.add_node("review", self._review_node)
        
        # Set entry point
        workflow.set_entry_point("init")
        
        # Add edges - optimized workflow
        workflow.add_edge("init", "extract_core_required")  # Start with required fields
        workflow.add_edge("extract_core_required", "extract_core_optional")  # Then optional fields
        workflow.add_edge("extract_core_optional", "suggest_special_schemas")  # Then suggest content type
        workflow.add_edge("suggest_special_schemas", "extract_special_required")  # Extract special required fields
        workflow.add_edge("extract_special_required", "extract_special_optional")  # Extract special optional fields
        
        # Conditional edge after special optional: more schemas or review?
        workflow.add_conditional_edges(
            "extract_special_optional",
            self._route_after_special_optional,
            {
                "next_schema": "extract_special_required",  # Process next special schema
                "review": "review"  # All schemas done, go to review
            }
        )
        
        workflow.add_edge("review", END)
        
        return workflow.compile()
    
    def _route_after_special_optional(self, state: WorkflowState) -> str:
        """Route after special optional: check if more special schemas to process."""
        if state.current_special_schema_index < len(state.special_schemas) - 1:
            # More schemas to process
            state.current_special_schema_index += 1
            state.special_required_complete = False
            state.special_optional_complete = False
            return "next_schema"
        else:
            # All schemas processed
            return "review"
    
    def _init_node(self, state: WorkflowState) -> WorkflowState:
        """Initialize the workflow."""
        state.phase = WorkflowPhase.INIT
        
        # Load core schema and initialize field statuses
        core_fields = self.schema_manager.get_fields("core.json")
        for field in core_fields:
            state.field_status[field.id] = FieldStatus(
                field_id=field.id,
                field_label=field.prompt.get("label", field.id),
                is_required=field.required,
                needs_user_input=field.ask_user
            )
        
        # Initialize metadata with empty template
        template = self.schema_manager.get_output_template("core.json")
        state.metadata = template.copy()
        
        state.add_message(
            "assistant",
            "👋 Willkommen! Ich helfe Ihnen beim Erstellen von Metadaten.\n\n"
            "📝 Bitte beschreiben Sie die Ressource, die Sie dokumentieren möchten. "
            "Je mehr Details Sie angeben, desto besser kann ich die Metadaten extrahieren."
        )
        
        return state
    
    def _suggest_special_schemas_node(self, state: WorkflowState, skip_history: bool = False) -> WorkflowState:
        """Suggest special schemas based on content type - AFTER core fields complete."""
        state.phase = WorkflowPhase.SUGGEST_SPECIAL_SCHEMAS
        if not skip_history:
            state.save_phase_to_history()
        
        # Only suggest if core optional is complete
        if not state.core_optional_complete:
            state.special_schema_confirmed = True
            return state
        
        # Get available special schemas
        try:
            available_schemas = self.schema_manager.get_available_special_schemas()
        except Exception as e:
            print(f"⚠️ Fehler beim Laden der verfügbaren Schemata: {e}")
            state.special_schema_confirmed = True
            state.add_message(
                "assistant",
                "✅ Core-Felder erfasst. Fahre fort ohne Spezial-Schema."
            )
            return state
        
        if not available_schemas:
            state.special_schema_confirmed = True
            state.add_message(
                "assistant",
                "✅ Alle Core-Felder sind erfasst! Keine weiteren Spezial-Schemata verfügbar."
            )
            return state
        
        # Try to detect content type from user input
        user_text = " ".join([msg.content for msg in state.messages if msg.role == "user"])
        
        if user_text:
            # Use LLM to suggest content types
            try:
                suggested_types = self._detect_content_types(user_text, list(available_schemas.keys()))
            except Exception as e:
                print(f"⚠️ Fehler bei Inhaltstyp-Erkennung: {e}")
                suggested_types = []
            
            if suggested_types:
                state.selected_content_types = suggested_types
                
                # Get corresponding schema files and verify they exist
                valid_schemas = []
                for content_type in suggested_types:
                    schema_file = available_schemas.get(content_type)
                    if schema_file:
                        # Check if file exists
                        import os
                        schema_path = os.path.join(self.schema_manager.schema_dir, schema_file)
                        if os.path.exists(schema_path):
                            if schema_file not in state.special_schemas:
                                state.special_schemas.append(schema_file)
                                valid_schemas.append(content_type)
                        else:
                            print(f"⚠️ Schema '{schema_file}' wurde nicht gefunden. Überspringe...")
                
                if valid_schemas:
                    types_str = ", ".join(valid_schemas)
                    state.add_message(
                        "assistant",
                        f"📋 Ich erkenne folgende Inhaltsart: **{types_str}**\n\n"
                        f"❓ Soll ich das entsprechende Spezial-Schema laden? (ja/nein)"
                    )
                else:
                    state.add_message(
                        "assistant",
                        "⚠️ Die erkannten Inhaltsarten haben noch keine Schemata. "
                        "Fahren Sie mit 'weiter' fort."
                    )
                    state.special_schema_confirmed = True
            else:
                # Ask user to select with numbers
                schema_list = list(available_schemas.keys())
                types_list = "\n".join([f"{i+1}. {t}" for i, t in enumerate(schema_list)])
                state.add_message(
                    "assistant",
                    f"📋 Welche Inhaltsart beschreiben Sie?\n\n{types_list}\n\n"
                    f"💡 Geben Sie die **Nummer** oder den **Namen** ein (z.B. '1' oder 'Organisation').\n"
                    f"Mehrfachauswahl mit Komma (z.B. '1,3' oder 'Organisation, Person').\n"
                    f"Oder 'keine' für keine Spezialfelder."
                )
                # Store schema list for number selection
                state.metadata["_temp_schema_list"] = schema_list
        
        return state
    
    def _extract_core_required_node(self, state: WorkflowState, skip_history: bool = False, skip_completion: bool = False) -> WorkflowState:
        """Extract core required fields using GPT-5."""
        state.phase = WorkflowPhase.EXTRACT_CORE_REQUIRED
        if not skip_history:
            state.save_phase_to_history()
        
        # Get required fields
        required_fields = self.schema_manager.get_required_fields("core.json")
        ai_fillable = [f for f in required_fields if f.ai_fillable]
        
        # Get user text
        user_text = " ".join([msg.content for msg in state.messages if msg.role == "user"])
        
        if user_text and ai_fillable:
            # Extract metadata using GPT-5
            extracted = self._extract_fields(user_text, ai_fillable, state.metadata)
            
            # Update state - mark as AI-suggested (needs confirmation)
            for field_id, value in extracted.items():
                state.update_field(field_id, value, confirmed=False, ai_suggested=True)
        
        # Build overview of all required fields
        message_parts = ["📝 **Pflichtfelder (Core-Schema):**\n"]
        
        filled_fields = []
        unfilled_fields = []
        
        for field in required_fields:
            field_status = state.field_status.get(field.id)
            label = field.prompt.get("label", field.id)
            
            if field_status and field_status.is_filled:
                # Show extracted value
                value_str = str(field_status.value)
                if isinstance(field_status.value, list):
                    value_str = ", ".join([str(v) for v in field_status.value])
                if len(value_str) > 100:
                    value_str = value_str[:100] + "..."
                filled_fields.append(f"✅ **{label}**: {value_str}")
            else:
                # Field missing
                description = field.prompt.get("description", "Bitte angeben")
                unfilled_fields.append(f"❌ **{label}**: {description}")
        
        # Add filled fields
        if filled_fields:
            message_parts.extend(filled_fields)
        
        # Add unfilled fields
        if unfilled_fields:
            message_parts.append("\n🔴 **Fehlende Pflichtfelder:**")
            message_parts.extend(unfilled_fields)
        
        # Check if all required fields are filled
        if not unfilled_fields:
            if not skip_completion:
                state.core_required_complete = True
            message_parts.append("\n✅ Alle Pflichtfelder sind erfasst!")
            message_parts.append("\n💬 **Bitte bestätigen Sie die Daten** oder korrigieren Sie Werte.")
            message_parts.append("Schreiben Sie 'ok' oder 'weiter' zum Fortfahren mit optionalen Feldern.")
            message_parts.append("Schreiben Sie 'zurück' um zum letzten Schritt zurückzukehren.")
        else:
            message_parts.append("\n💬 Bitte überprüfen Sie die Werte und ergänzen/korrigieren Sie fehlende Angaben.")
        
        state.add_message("assistant", "\n".join(message_parts))
        
        return state
    
    def _extract_core_optional_node(self, state: WorkflowState, skip_history: bool = False, skip_completion: bool = False) -> WorkflowState:
        """Extract core optional fields."""
        state.phase = WorkflowPhase.EXTRACT_CORE_OPTIONAL
        if not skip_history:
            state.save_phase_to_history()
        
        if not state.core_required_complete:
            return state
        
        # Get optional fields (not required)
        optional_fields = self.schema_manager.get_optional_fields("core.json")
        ai_fillable = [f for f in optional_fields if f.ai_fillable]
        
        # Get user text
        user_text = " ".join([msg.content for msg in state.messages if msg.role == "user"])
        
        if user_text and ai_fillable:
            # Extract metadata using GPT-5
            extracted = self._extract_fields(user_text, ai_fillable, state.metadata)
            
            # Update state
            for field_id, value in extracted.items():
                if value:  # Only update if there's a value
                    state.update_field(field_id, value, confirmed=False, ai_suggested=True)
        
        # Build overview of optional fields
        message_parts = ["📋 **Optionale Felder (Core-Schema):**\n"]
        
        # List available optional field names
        field_names = [field.prompt.get("label", field.id) for field in optional_fields[:12]]
        message_parts.append(f"Verfügbare Felder: {', '.join(field_names)}\n")
        
        filled_optional = []
        important_empty = []
        
        # Show filled and important empty fields
        for field in optional_fields:
            field_status = state.field_status.get(field.id)
            label = field.prompt.get("label", field.id)
            
            if field_status and field_status.is_filled:
                value_str = str(field_status.value)
                if isinstance(field_status.value, list):
                    value_str = ", ".join([str(v) for v in field_status.value])
                if len(value_str) > 80:
                    value_str = value_str[:80] + "..."
                filled_optional.append(f"✅ **{label}**: {value_str}")
            else:
                # Show description for first 5 important fields
                description = field.prompt.get("description", "")
                if description and len(important_empty) < 5:
                    important_empty.append(f"⚪ **{label}**: {description}")
        
        if filled_optional:
            message_parts.append("**Bereits erfasst:**")
            message_parts.extend(filled_optional)
        
        if important_empty:
            message_parts.append("\n💡 **Beispiele für weitere Felder:**")
            message_parts.extend(important_empty)
        
        message_parts.append("\n💬 Möchten Sie optionale Felder ergänzen oder korrigieren?")
        message_parts.append("Geben Sie die Werte ein oder schreiben Sie 'weiter' zum Fortfahren.")
        message_parts.append("Schreiben Sie 'zurück' um zum letzten Schritt zurückzukehren.")
        
        state.add_message("assistant", "\n".join(message_parts))
        # Don't mark as complete yet - wait for user confirmation with 'weiter'
        return state
    
    def _extract_special_required_node(self, state: WorkflowState, skip_history: bool = False, skip_completion: bool = False) -> WorkflowState:
        """Extract required fields from CURRENT special schema."""
        state.phase = WorkflowPhase.EXTRACT_SPECIAL_REQUIRED
        if not skip_history:
            state.save_phase_to_history()
        
        if not state.special_schema_confirmed:
            state.special_required_complete = True
            return state
        
        if not state.special_schemas or state.current_special_schema_index >= len(state.special_schemas):
            # No schemas selected (user said no)
            state.special_required_complete = True
            state.add_message(
                "assistant",
                "✅ Core-Felder erfasst. Fahre fort zur Überprüfung."
            )
            return state
        
        # Get CURRENT special schema
        schema_file = state.special_schemas[state.current_special_schema_index]
        schema_number = state.current_special_schema_index + 1
        total_schemas = len(state.special_schemas)
        
        # Load special schema fields
        try:
            fields = self.schema_manager.get_fields(schema_file)
            
            # Initialize field statuses (only if first time seeing this schema)
            for field in fields:
                if field.id not in state.field_status:
                    state.field_status[field.id] = FieldStatus(
                        field_id=field.id,
                        field_label=field.prompt.get("label", field.id),
                        is_required=field.required,
                        needs_user_input=field.ask_user
                    )
            
            # Merge templates
            template = self.schema_manager.get_output_template(schema_file)
            state.metadata.update(template)
        except FileNotFoundError:
            state.add_message(
                "assistant",
                f"⚠️ Schema '{schema_file}' wurde nicht gefunden. Überspringe..."
            )
            state.special_required_complete = True
            return state
        
        # Inform user that schema was loaded
        schema_name = schema_file.replace('.json', '').replace('_', ' ').title()
        state.add_message(
            "assistant",
            f"✅ Spezial-Schema geladen: **{schema_name}** ({schema_number}/{total_schemas})\n\n"
            f"Extrahiere typspezifische Pflichtfelder..."
        )
        
        # Get required fields only
        required_fields = [f for f in fields if f.required]
        
        if not required_fields:
            # No required fields in this schema
            state.special_required_complete = True
            state.add_message(
                "assistant",
                f"✅ Keine Pflichtfelder im Schema '{schema_name}'."
            )
            return state
        
        ai_fillable = [f for f in required_fields if f.ai_fillable]
        
        # Get user text
        user_text = " ".join([msg.content for msg in state.messages if msg.role == "user"])
        
        if user_text and ai_fillable:
            # Extract metadata using GPT-5
            extracted = self._extract_fields(user_text, ai_fillable, state.metadata)
            
            # Update state - mark as AI-suggested (needs confirmation)
            for field_id, value in extracted.items():
                if value:
                    state.update_field(field_id, value, confirmed=False, ai_suggested=True)
        
        # Build overview of required special fields
        message_parts = [f"📝 **Pflichtfelder ({schema_name}):**\n"]
        
        filled_fields = []
        unfilled_fields = []
        
        for field in required_fields:
            field_status = state.field_status.get(field.id)
            label = field.prompt.get("label", field.id)
            
            if field_status and field_status.is_filled:
                # Show extracted value
                value_str = str(field_status.value)
                if isinstance(field_status.value, list):
                    value_str = ", ".join([str(v) for v in field_status.value])
                if len(value_str) > 100:
                    value_str = value_str[:100] + "..."
                filled_fields.append(f"✅ **{label}**: {value_str}")
            else:
                # Field missing
                description = field.prompt.get("description", "Bitte angeben")
                if not field.ai_fillable:
                    description += " (manuell auszufüllen)"
                unfilled_fields.append(f"❌ **{label}**: {description}")
        
        # Add filled fields
        if filled_fields:
            message_parts.extend(filled_fields)
        
        # Add unfilled fields
        if unfilled_fields:
            message_parts.append("\n🔴 **Fehlende typspezifische Pflichtfelder:**")
            message_parts.extend(unfilled_fields)
        
        # Check if all required fields are filled
        if not unfilled_fields:
            if not skip_completion:
                state.special_required_complete = True
            message_parts.append("\n✅ Alle typspezifischen Pflichtfelder sind erfasst!")
            message_parts.append("\n💬 **Sind diese Daten korrekt?**")
            message_parts.append("Schreiben Sie 'ok' oder 'weiter' zum Fortfahren mit optionalen Feldern,")
            message_parts.append("'zurück' für den letzten Schritt, oder korrigieren Sie die Werte.")
        else:
            message_parts.append("\n💬 Bitte überprüfen Sie die Werte und ergänzen/korrigieren Sie fehlende Angaben.")
            message_parts.append("Schreiben Sie 'zurück' um zum letzten Schritt zurückzukehren.")
        
        state.add_message("assistant", "\n".join(message_parts))
        
        return state
    
    def _extract_special_optional_node(self, state: WorkflowState, skip_history: bool = False, skip_completion: bool = False) -> WorkflowState:
        """Extract optional fields from CURRENT special schema."""
        state.phase = WorkflowPhase.EXTRACT_SPECIAL_OPTIONAL
        if not skip_history:
            state.save_phase_to_history()
        
        if not state.special_required_complete or not state.special_schemas:
            state.special_optional_complete = True
            return state
        
        if state.current_special_schema_index >= len(state.special_schemas):
            state.special_optional_complete = True
            return state
        
        # Get CURRENT special schema
        schema_file = state.special_schemas[state.current_special_schema_index]
        schema_name = schema_file.replace('.json', '').replace('_', ' ').title()
        schema_number = state.current_special_schema_index + 1
        total_schemas = len(state.special_schemas)
        
        # Get fields from current schema
        try:
            fields = self.schema_manager.get_fields(schema_file)
        except FileNotFoundError:
            state.special_optional_complete = True
            return state
        
        # Get optional fields (not required)
        optional_fields = [f for f in fields if not f.required]
        
        if not optional_fields:
            state.special_optional_complete = True
            
            # Check if more schemas to process
            if schema_number < total_schemas:
                state.add_message(
                    "assistant",
                    f"✅ Keine optionalen Felder im Schema '{schema_name}'.\n\n"
                    f"Fahre fort mit nächstem Schema..."
                )
            else:
                state.add_message(
                    "assistant",
                    f"✅ Keine optionalen Felder im Schema '{schema_name}'."
                )
            return state
        
        ai_fillable = [f for f in optional_fields if f.ai_fillable]
        
        # Get user text
        user_text = " ".join([msg.content for msg in state.messages if msg.role == "user"])
        
        if user_text and ai_fillable:
            # Extract metadata using GPT-5
            extracted = self._extract_fields(user_text, ai_fillable, state.metadata)
            
            # Update state
            for field_id, value in extracted.items():
                if value:  # Only update if there's a value
                    state.update_field(field_id, value, confirmed=False, ai_suggested=True)
        
        # Build overview of optional special fields
        message_parts = [f"📋 **Optionale Felder ({schema_name}):** ({schema_number}/{total_schemas})\n"]
        
        # List available optional field names
        field_names = [field.prompt.get("label", field.id) for field in optional_fields[:8]]
        message_parts.append(f"Verfügbare Felder: {', '.join(field_names)}\n")
        
        filled_optional = []
        important_empty = []
        
        # Show filled and important empty fields
        for field in optional_fields:
            field_status = state.field_status.get(field.id)
            label = field.prompt.get("label", field.id)
            
            if field_status and field_status.is_filled:
                value_str = str(field_status.value)
                if isinstance(field_status.value, list):
                    value_str = ", ".join([str(v) for v in field_status.value])
                if len(value_str) > 80:
                    value_str = value_str[:80] + "..."
                filled_optional.append(f"✅ **{label}**: {value_str}")
            else:
                # Show description for first 5 important fields
                description = field.prompt.get("description", "")
                if description and len(important_empty) < 5:
                    if not field.ai_fillable:
                        description += " (manuell auszufüllen)"
                    important_empty.append(f"⚪ **{label}**: {description}")
        
        if filled_optional:
            message_parts.append("**Bereits erfasst:**")
            message_parts.extend(filled_optional)
        
        if important_empty:
            message_parts.append("\n💡 **Beispiele für weitere Felder:**")
            message_parts.extend(important_empty)
        
        # Check if more schemas to process
        if schema_number < total_schemas:
            message_parts.append("\n💬 Möchten Sie optionale Felder ergänzen oder korrigieren?")
            message_parts.append("Geben Sie die Werte ein oder schreiben Sie 'weiter' für das nächste Schema.")
            message_parts.append("Schreiben Sie 'zurück' um zum letzten Schritt zurückzukehren.")
        else:
            message_parts.append("\n💬 Möchten Sie optionale Felder ergänzen oder korrigieren?")
            message_parts.append("Geben Sie die Werte ein oder schreiben Sie 'weiter' zum Abschließen.")
            message_parts.append("Schreiben Sie 'zurück' um zum letzten Schritt zurückzukehren.")
        
        state.add_message("assistant", "\n".join(message_parts))
        # Don't mark as complete yet - wait for user confirmation with 'weiter'
        return state
    
    def _review_node(self, state: WorkflowState, skip_history: bool = False) -> WorkflowState:
        """Review and finalize metadata."""
        state.phase = WorkflowPhase.REVIEW
        if not skip_history:
            state.save_phase_to_history()
        
        # Compile final metadata
        final_metadata = {}
        for field_id, status in state.field_status.items():
            if status.is_filled:
                final_metadata[field_id] = status.value
        
        state.metadata = final_metadata
        
        state.add_message(
            "assistant",
            "✅ Metadatenextraktion abgeschlossen! Sie können das Ergebnis im JSON-Vorschaubereich sehen."
        )
        
        # Count fields by type
        core_fields = [f for f in final_metadata.keys() if f.startswith('cclom:')]
        special_fields = [f for f in final_metadata.keys() if not f.startswith('cclom:')]
        
        state.add_message(
            "assistant",
            f"📊 **Metadaten-Übersicht:**\n\n"
            f"✅ Core-Felder: {len(core_fields)}\n"
            f"✅ Spezial-Felder: {len(special_fields)}\n\n"
            f"💬 **Bitte überprüfen Sie die Daten im JSON-Vorschaubereich.**\n"
            f"Schreiben Sie 'bestätigen' zum Abschluss oder korrigieren Sie Werte."
        )
        
        state.phase = WorkflowPhase.COMPLETE
        return state
    
    def _call_gpt5(self, input_text: str, reasoning_effort: str = None, verbosity: str = None) -> Dict[str, Any]:
        """Call LLM API - uses GPT-5 Responses API for gpt-5* models, Chat Completions API for others."""
        
        try:
            if self.is_gpt5:
                # GPT-5 models: Use Responses API with reasoning and verbosity
                reasoning_effort = reasoning_effort or self.default_reasoning_effort
                verbosity = verbosity or self.default_verbosity
                
                response = self.client.responses.create(
                    model=self.model,
                    input=input_text,
                    reasoning={"effort": reasoning_effort},
                    text={"verbosity": verbosity}
                )
                return {
                    "output_text": response.output_text,
                    "response_id": response.id,
                    "tokens": response.usage.total_tokens
                }
            else:
                # Other models (GPT-4, GPT-3.5, etc.): Use standard Chat Completions API
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": input_text}],
                    temperature=0.1  # Low temperature for consistent extraction
                )
                return {
                    "output_text": response.choices[0].message.content,
                    "response_id": response.id,
                    "tokens": response.usage.total_tokens
                }
        except Exception as e:
            print(f"LLM API Error: {e}")
            return {"output_text": f"Error: {str(e)}", "response_id": None, "tokens": 0}
    
    def _detect_content_types(self, text: str, available_types: List[str]) -> List[str]:
        """Use GPT-5 to detect content types from text."""
        if not available_types:
            return []
        
        prompt = f"""Analysiere folgenden Text und identifiziere die passende Inhaltsart:

Text: {text}

Verfügbare Inhaltsarten:
{chr(10).join(available_types)}

Antworte nur mit EINEM Wort aus der Liste der verfügbaren Inhaltsarten.
Wähle die am besten passende Kategorie."""
        
        try:
            response = self._call_gpt5(prompt, reasoning_effort="minimal", verbosity="low")
            content = response["output_text"].strip()
            
            # Parse response (could be comma-separated even though we ask for one)
            detected = [t.strip() for t in content.replace(",", " ").split()]
            
            # Filter to only valid types
            valid = [t for t in detected if t in available_types]
            return valid[:1]  # Return only 1 type
        except Exception as e:
            print(f"Error detecting content types: {e}")
            return []
    
    def _validate_and_normalize_fields(self, extracted: Dict[str, Any], fields: List[Field]) -> tuple:
        """
        Validate and normalize extracted field values.
        
        Returns:
            tuple: (normalized_data, validation_warnings)
        """
        normalized = {}
        warnings = []
        
        # Create field lookup
        field_map = {f.id: f for f in fields}
        
        for field_id, value in extracted.items():
            field = field_map.get(field_id)
            if not field:
                warnings.append(f"⚠️ Unbekanntes Feld: {field_id}")
                continue
            
            try:
                # Normalize the value according to schema rules
                normalized_value = self.validator.normalize_value(value, field)
                
                # Validate vocabulary if defined
                if field.vocabulary and normalized_value:
                    vocab_type = field.vocabulary.get("type", "open")
                    concepts = field.get_vocabulary_concepts()
                    
                    if vocab_type == "closed" and concepts:
                        # Check if value is in allowed concepts
                        allowed_labels = [c.get("label", "") for c in concepts]
                        
                        if isinstance(normalized_value, list):
                            invalid = [v for v in normalized_value if v not in allowed_labels]
                            if invalid:
                                warnings.append(
                                    f"⚠️ **{field.prompt.get('label', field_id)}**: "
                                    f"Ungültige Werte: {', '.join(invalid)}\n"
                                    f"   Erlaubt: {', '.join(allowed_labels[:5])}{'...' if len(allowed_labels) > 5 else ''}"
                                )
                        else:
                            if normalized_value not in allowed_labels:
                                warnings.append(
                                    f"⚠️ **{field.prompt.get('label', field_id)}**: "
                                    f"'{normalized_value}' ist nicht in der erlaubten Liste.\n"
                                    f"   Erlaubt: {', '.join(allowed_labels[:5])}{'...' if len(allowed_labels) > 5 else ''}"
                                )
                
                # Validate datatype
                expected_type = field.datatype
                if expected_type == "string" and not isinstance(normalized_value, (str, list)):
                    warnings.append(f"⚠️ **{field.prompt.get('label', field_id)}**: Erwartet Text, erhalten {type(normalized_value).__name__}")
                elif expected_type == "date" and isinstance(normalized_value, str):
                    # Basic date validation
                    if not re.match(r'^\d{4}-\d{2}-\d{2}', normalized_value):
                        warnings.append(f"⚠️ **{field.prompt.get('label', field_id)}**: Ungültiges Datumsformat (erwartet: YYYY-MM-DD)")
                
                normalized[field_id] = normalized_value
                
            except Exception as e:
                warnings.append(f"⚠️ Fehler bei **{field.prompt.get('label', field_id)}**: {str(e)}")
                normalized[field_id] = value  # Use original value on error
        
        return normalized, warnings
    
    def _extract_fields(self, text: str, fields: List[Field], current_metadata: Dict) -> Dict[str, Any]:
        """Extract field values from text using GPT-5."""
        # Build field descriptions for prompt
        field_descriptions = []
        for field in fields:
            label = field.prompt.get("label", field.id)
            description = field.prompt.get("description", "")
            datatype = field.datatype
            multiple = "Liste" if field.multiple else "Einzelwert"
            
            vocab_info = ""
            if field.vocabulary:
                concepts = field.get_vocabulary_concepts()
                if concepts and len(concepts) < 20:  # Only show if not too many
                    vocab_labels = [c.get("label", "") for c in concepts[:10]]
                    vocab_info = f" Mögliche Werte: {', '.join(vocab_labels)}"
            
            field_descriptions.append(
                f"- **{field.id}** ({label}): {description} [{datatype}, {multiple}]{vocab_info}"
            )
        
        prompt = f"""Du bist ein Experte für Metadatenextraktion aus Bildungsinhalten.
Extrahiere strukturierte Metadaten aus dem Text.
Antworte NUR mit einem validen JSON-Objekt, ohne zusätzlichen Text.

Extrahiere folgende Felder aus dem Text:

{chr(10).join(field_descriptions)}

Text:
{text}

Antworte mit einem JSON-Objekt mit den Feldnamen als Keys.
Verwende null für Felder, die nicht extrahiert werden können.
Für Listen verwende Arrays. Für Einzelwerte verwende Strings."""
        
        try:
            response = self._call_gpt5(prompt, reasoning_effort="minimal", verbosity="low")
            content = response["output_text"].strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                extracted = json.loads(json_match.group())
                # Filter out null values
                raw_extracted = {k: v for k, v in extracted.items() if v is not None}
                
                # Validate and normalize
                normalized, validation_warnings = self._validate_and_normalize_fields(raw_extracted, fields)
                
                # Log warnings
                if validation_warnings:
                    print(f"🔍 Validierung: {len(validation_warnings)} Warnungen")
                    for w in validation_warnings:
                        print(f"  {w}")
                
                return normalized
            else:
                return {}
        except Exception as e:
            print(f"Error extracting fields: {e}")
            return {}
    
    def process_user_input(self, state: WorkflowState, user_input: str) -> WorkflowState:
        """Process user input and update state."""
        state.add_message("user", user_input)
        state.user_input = user_input
        
        # Check for back navigation first
        if user_input.lower().strip() in ["zurück", "back", "zurück", "zurueck"]:
            if state.go_back_phase():
                # Reset completion flags based on phase
                if state.phase == WorkflowPhase.EXTRACT_CORE_REQUIRED:
                    state.core_required_complete = False
                    state.add_message("assistant", "⬅️ Zurück zu: **Core-Pflichtfelder**\n")
                    # Re-run node to show fields again (skip history and completion to avoid auto-advance)
                    state = self._extract_core_required_node(state, skip_history=True, skip_completion=True)
                    
                elif state.phase == WorkflowPhase.EXTRACT_CORE_OPTIONAL:
                    state.core_optional_complete = False
                    state.add_message("assistant", "⬅️ Zurück zu: **Core-Optionale Felder**\n")
                    # Re-run node to show fields again (skip history and completion to avoid auto-advance)
                    state = self._extract_core_optional_node(state, skip_history=True, skip_completion=True)
                    
                elif state.phase == WorkflowPhase.SUGGEST_SPECIAL_SCHEMAS:
                    state.special_schema_confirmed = False
                    state.add_message("assistant", "⬅️ Zurück zu: **Spezialschema-Auswahl**\n")
                    # Re-run node to show schema suggestions again (skip history to avoid duplicate)
                    state = self._suggest_special_schemas_node(state, skip_history=True)
                    
                elif state.phase == WorkflowPhase.EXTRACT_SPECIAL_REQUIRED:
                    state.special_required_complete = False
                    # Go back to previous schema if we're not on the first one
                    if state.current_special_schema_index > 0:
                        state.current_special_schema_index -= 1
                    state.add_message("assistant", "⬅️ Zurück zu: **Spezial-Pflichtfelder**\n")
                    # Re-run node to show fields again (skip history and completion to avoid auto-advance)
                    state = self._extract_special_required_node(state, skip_history=True, skip_completion=True)
                    
                elif state.phase == WorkflowPhase.EXTRACT_SPECIAL_OPTIONAL:
                    state.special_optional_complete = False
                    state.add_message("assistant", "⬅️ Zurück zu: **Spezial-Optionale Felder**\n")
                    # Re-run node to show fields again (skip history and completion to avoid auto-advance)
                    state = self._extract_special_optional_node(state, skip_history=True, skip_completion=True)
                    
                elif state.phase == WorkflowPhase.REVIEW:
                    state.add_message("assistant", "⬅️ Zurück zu: **Review**\n")
                    # Re-run review node (skip history to avoid duplicate)
                    state = self._review_node(state, skip_history=True)
            else:
                state.add_message(
                    "assistant",
                    "⚠️ Sie sind bereits am Anfang des Workflows."
                )
            return state
        
        # Handle phase-specific logic
        if state.phase == WorkflowPhase.SUGGEST_SPECIAL_SCHEMAS:
            # Check for confirmation or schema selection
            if any(word in user_input.lower() for word in ["ja", "yes", "korrekt", "richtig"]):
                state.special_schema_confirmed = True
                # Don't add message here - will be added by _extract_special_schema_node
            elif any(word in user_input.lower() for word in ["nein", "no", "nicht", "keine"]):
                state.special_schema_confirmed = True
                state.special_schemas = []  # Clear selected schemas
                state.add_message("assistant", "✅ Fahre fort ohne Spezial-Schema.")
            else:
                # Try to extract content type from input (number or name)
                try:
                    available = self.schema_manager.get_available_special_schemas()
                    schema_list = state.metadata.get("_temp_schema_list", list(available.keys()))
                    
                    # Parse user input - could be numbers or names, comma-separated
                    selections = [s.strip() for s in user_input.replace(",", " ").split()]
                    
                    for selection in selections:
                        # Check if it's a number (1-based index)
                        if selection.isdigit():
                            idx = int(selection) - 1
                            if 0 <= idx < len(schema_list):
                                content_type = schema_list[idx]
                                schema_file = available.get(content_type)
                                if schema_file:
                                    if content_type not in state.selected_content_types:
                                        state.selected_content_types.append(content_type)
                                    if schema_file not in state.special_schemas:
                                        state.special_schemas.append(schema_file)
                        else:
                            # Try to match by name (flexible matching)
                            selection_lower = selection.lower()
                            for content_type, schema_file in available.items():
                                # Match if selection is substring of content_type or vice versa
                                if (selection_lower in content_type.lower() or 
                                    content_type.lower() in selection_lower):
                                    if content_type not in state.selected_content_types:
                                        state.selected_content_types.append(content_type)
                                    if schema_file not in state.special_schemas:
                                        state.special_schemas.append(schema_file)
                                    break  # Only match first one
                    
                    if state.selected_content_types:
                        state.special_schema_confirmed = True
                        # Clean up temp data
                        if "_temp_schema_list" in state.metadata:
                            del state.metadata["_temp_schema_list"]
                    else:
                        state.add_message(
                            "assistant",
                            "⚠️ Keine passende Inhaltsart gefunden. Bitte versuchen Sie es erneut oder schreiben Sie 'keine'."
                        )
                except Exception as e:
                    print(f"⚠️ Fehler bei Schema-Auswahl: {e}")
                    state.special_schema_confirmed = True
                    state.add_message("assistant", "⚠️ Fehler bei Schema-Auswahl. Fahre fort ohne Spezial-Schema.")
        
        elif state.phase in [WorkflowPhase.EXTRACT_CORE_REQUIRED, WorkflowPhase.EXTRACT_CORE_OPTIONAL, 
                             WorkflowPhase.EXTRACT_SPECIAL_REQUIRED, WorkflowPhase.EXTRACT_SPECIAL_OPTIONAL]:
            
            # Check if user wants to move forward first (before extracting)
            user_input_lower = user_input.lower().strip()
            is_navigation_command = user_input_lower in ["weiter", "next", "fortfahren", "skip", "ok", "okay"]
            
            # Check if user is providing corrections/additions
            is_correction = not is_navigation_command and len(user_input) > 2
            
            # Only extract/update fields if user is providing corrections
            if is_correction:
                # Reset completion flags when user provides corrections
                if state.phase == WorkflowPhase.EXTRACT_CORE_REQUIRED:
                    state.core_required_complete = False
                elif state.phase == WorkflowPhase.EXTRACT_CORE_OPTIONAL:
                    state.core_optional_complete = False
                elif state.phase == WorkflowPhase.EXTRACT_SPECIAL_REQUIRED:
                    state.special_required_complete = False
                elif state.phase == WorkflowPhase.EXTRACT_SPECIAL_OPTIONAL:
                    state.special_optional_complete = False
                # Try to extract field values from input
                if state.phase == WorkflowPhase.EXTRACT_CORE_REQUIRED:
                    fields = self.schema_manager.get_required_fields("core.json")
                elif state.phase == WorkflowPhase.EXTRACT_CORE_OPTIONAL:
                    fields = self.schema_manager.get_optional_fields("core.json")
                elif state.phase == WorkflowPhase.EXTRACT_SPECIAL_REQUIRED:
                    # Get required fields from CURRENT special schema
                    fields = []
                    if state.current_special_schema_index < len(state.special_schemas):
                        schema_file = state.special_schemas[state.current_special_schema_index]
                        try:
                            schema_fields = self.schema_manager.get_fields(schema_file)
                            fields = [f for f in schema_fields if f.required]
                        except FileNotFoundError:
                            pass
                elif state.phase == WorkflowPhase.EXTRACT_SPECIAL_OPTIONAL:
                    # Get optional fields from CURRENT special schema
                    fields = []
                    if state.current_special_schema_index < len(state.special_schemas):
                        schema_file = state.special_schemas[state.current_special_schema_index]
                        try:
                            schema_fields = self.schema_manager.get_fields(schema_file)
                            fields = [f for f in schema_fields if not f.required]
                        except FileNotFoundError:
                            pass
                
                # Extract fields
                extracted = self._extract_fields(user_input, fields, state.metadata)
                for field_id, value in extracted.items():
                    state.update_field(field_id, value, confirmed=True)
                
                # After corrections, re-display the fields to show updated values
                state.add_message(
                    "assistant",
                    "✅ Ich habe Ihre Änderungen verarbeitet. Hier die aktualisierten Daten:\n"
                )
                
                # Re-run the node to show updated fields (skip history and completion to avoid auto-advance)
                if state.phase == WorkflowPhase.EXTRACT_CORE_REQUIRED:
                    state = self._extract_core_required_node(state, skip_history=True, skip_completion=True)
                elif state.phase == WorkflowPhase.EXTRACT_CORE_OPTIONAL:
                    state = self._extract_core_optional_node(state, skip_history=True, skip_completion=True)
                elif state.phase == WorkflowPhase.EXTRACT_SPECIAL_REQUIRED:
                    state = self._extract_special_required_node(state, skip_history=True, skip_completion=True)
                elif state.phase == WorkflowPhase.EXTRACT_SPECIAL_OPTIONAL:
                    state = self._extract_special_optional_node(state, skip_history=True, skip_completion=True)
                
                return state  # Don't proceed to navigation, just show updated fields
            
            # Check if we can move forward
            if is_navigation_command:
                if state.phase == WorkflowPhase.EXTRACT_CORE_REQUIRED:
                    unfilled = state.get_unfilled_required_fields()
                    core_required = ["cclom:title", "cclom:general_description", "cclom:general_keyword"]
                    missing_core = [f for f in core_required if f in unfilled]
                    if not missing_core:
                        state.core_required_complete = True
                        # Don't add message here - will be added by next node
                elif state.phase == WorkflowPhase.EXTRACT_CORE_OPTIONAL:
                    state.core_optional_complete = True
                    # Don't add message here - will be added by _suggest_special_schemas_node
                elif state.phase == WorkflowPhase.EXTRACT_SPECIAL_REQUIRED:
                    # Check if all required fields of CURRENT schema are filled
                    if state.current_special_schema_index < len(state.special_schemas):
                        schema_file = state.special_schemas[state.current_special_schema_index]
                        try:
                            schema_fields = self.schema_manager.get_fields(schema_file)
                            special_required_fields = [f.id for f in schema_fields if f.required]
                            
                            unfilled = [f for f in special_required_fields if f not in state.field_status or not state.field_status[f].is_filled]
                            if not unfilled:
                                state.special_required_complete = True
                                # Don't add message here - will be added by next node
                        except FileNotFoundError:
                            state.special_required_complete = True
                elif state.phase == WorkflowPhase.EXTRACT_SPECIAL_OPTIONAL:
                    state.special_optional_complete = True
                    # Don't add message here - will be added by next node or review
        
        return state
