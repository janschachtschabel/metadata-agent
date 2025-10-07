"""Minimale Gradio UI für Metadatenextraktion - optimiert für Seitenleiste."""
import gradio as gr
import json
import os
from dotenv import load_dotenv
from agent import MetadataAgent
from models import WorkflowState
from schema_loader import SchemaManager

# Load environment
load_dotenv()

# Initialize agent and schema manager
agent = MetadataAgent()
schema_manager = SchemaManager()

# Get available content types (exclude core.json)
available_schemas = schema_manager.get_available_special_schemas()
content_type_choices = ["Automatisch"] + list(available_schemas.keys())

# Schema file mapping
schema_file_map = {label: file for label, file in available_schemas.items()}


def extract_metadata(text: str, content_type: str) -> tuple:
    """
    Extract metadata from text.
    
    Args:
        text: Input text
        content_type: Selected content type ("Automatisch" or specific type)
    
    Returns:
        (metadata_json, status_message)
    """
    if not text or not text.strip():
        return "", "⚠️ Bitte Text eingeben"
    
    try:
        state = WorkflowState()
        state.add_message("user", text)
        
        # Phase 1: Init
        state = agent._init_node(state)
        
        # Phase 2: Core Required
        state = agent._extract_core_required_node(state)
        state.core_required_complete = True
        
        # Phase 3: Core Optional
        state = agent._extract_core_optional_node(state)
        state.core_optional_complete = True
        
        # Phase 4: Schema Detection
        if content_type == "Automatisch":
            # Automatic detection
            state = agent._suggest_special_schemas_node(state)
            if state.selected_content_types:
                state.selected_content_types = state.selected_content_types[:1]
                state.special_schemas = state.special_schemas[:1]
                detected_type = state.selected_content_types[0]
                status_msg = f"🔍 Erkannte Inhaltsart: **{detected_type}**"
            else:
                status_msg = "✅ Nur Core-Felder extrahiert (keine Inhaltsart erkannt)"
            state.special_schema_confirmed = True
        else:
            # Manual selection
            schema_file = schema_file_map.get(content_type)
            if schema_file:
                state.selected_content_types = [content_type]
                state.special_schemas = [schema_file]
                state.special_schema_confirmed = True
                status_msg = f"📋 Gewählte Inhaltsart: **{content_type}**"
            else:
                status_msg = f"⚠️ Schema für '{content_type}' nicht gefunden"
        
        # Phase 5: Special Schema Fields
        if state.special_schemas:
            # 5a: Required
            state = agent._extract_special_required_node(state)
            state.special_required_complete = True
            
            # 5b: Optional
            state = agent._extract_special_optional_node(state)
            state.special_optional_complete = True
        
        # Phase 6: Review
        state = agent._review_node(state)
        
        # Extract final metadata
        final_metadata = {k: v for k, v in state.metadata.items() if v and not k.startswith("_")}
        
        # Count fields
        filled_count = len([f for f in state.field_status.values() if f.is_filled])
        status_msg += f"\n\n✅ **{filled_count} Felder** extrahiert"
        
        # Format as JSON
        metadata_json = json.dumps(final_metadata, ensure_ascii=False, indent=2)
        
        return metadata_json, status_msg
        
    except Exception as e:
        return "", f"❌ Fehler: {str(e)}"


def revise_metadata(text: str, current_metadata: str, revision_request: str, content_type: str) -> tuple:
    """
    Revise metadata based on user feedback.
    
    Re-runs the full extraction workflow with original text + current metadata + revision request.
    This ensures all schema validations and vocabularies are applied correctly.
    
    Args:
        text: Original input text
        current_metadata: Current metadata JSON
        revision_request: User's revision request
        content_type: Selected content type
    
    Returns:
        (updated_metadata_json, status_message)
    """
    if not revision_request or not revision_request.strip():
        return current_metadata, "⚠️ Bitte Änderungswunsch eingeben"
    
    if not current_metadata:
        return "", "⚠️ Erst Metadaten extrahieren"
    
    try:
        # Parse current metadata for context
        metadata = json.loads(current_metadata)
        
        # Build combined input text with current metadata and revision request
        combined_text = f"""ORIGINALTEXT:
{text}

AKTUELLE METADATEN:
{json.dumps(metadata, ensure_ascii=False, indent=2)}

ÄNDERUNGSWUNSCH:
{revision_request}

Bitte aktualisiere die Metadaten gemäß dem Änderungswunsch. Behalte alle Felder bei, die nicht geändert werden sollen."""

        # Run full extraction workflow with combined input
        # This ensures all schema validations and vocabularies are applied
        updated_metadata_json, status_msg = extract_metadata(combined_text, content_type)
        
        if updated_metadata_json:
            return updated_metadata_json, f"✅ Metadaten überarbeitet\n\n💬 Änderung: {revision_request}\n\n{status_msg}"
        else:
            return current_metadata, f"⚠️ Fehler bei der Überarbeitung: {status_msg}"
            
    except json.JSONDecodeError:
        return current_metadata, "❌ Fehler beim Parsen der aktuellen Metadaten"
    except Exception as e:
        return current_metadata, f"❌ Fehler: {str(e)}"


def save_json(metadata_json: str) -> str:
    """Save metadata to file and return download path."""
    if not metadata_json:
        return None
    
    try:
        # Create output directory if not exists
        os.makedirs("output", exist_ok=True)
        
        # Generate filename with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"output/metadata_{timestamp}.json"
        
        # Parse and save
        metadata = json.loads(metadata_json)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        return filename
    except Exception as e:
        print(f"Error saving JSON: {e}")
        return None


# Build Gradio UI
with gr.Blocks(title="Metadaten-Extraktion (Minimal)", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 Metadaten-Extraktion")
    gr.Markdown("Kompakte Version für Seitenleiste")
    
    with gr.Column():
        # Input text
        input_text = gr.Textbox(
            label="📝 Text eingeben",
            placeholder="Beschreiben Sie die Ressource...",
            lines=8,
            max_lines=8,
            elem_id="input_box"
        )
        
        # Content type selection
        content_type_dropdown = gr.Dropdown(
            label="🔍 Inhaltsart",
            choices=content_type_choices,
            value="Automatisch",
            interactive=True
        )
        
        # Extract button
        extract_btn = gr.Button("▶️ Metadaten extrahieren", variant="primary", size="sm")
        
        # Status message
        status_output = gr.Markdown("", elem_id="status")
        
        # Metadata preview (same size as input)
        metadata_output = gr.Code(
            label="📋 Metadaten (JSON)",
            language="json",
            lines=8,
            interactive=False,
            elem_id="metadata_box"
        )
        
        # Revision section
        with gr.Accordion("✏️ Änderungen vornehmen", open=False):
            revision_input = gr.Textbox(
                label="Änderungswunsch",
                placeholder="z.B. 'Ändere den Titel zu...' oder 'Füge Autor hinzu: ...'",
                lines=2
            )
            revise_btn = gr.Button("🔄 Überarbeiten", size="sm")
        
        # Download button
        download_btn = gr.Button("💾 JSON speichern", size="sm")
        download_file = gr.File(label="Download", visible=False)
    
    # Event handlers
    extract_btn.click(
        fn=extract_metadata,
        inputs=[input_text, content_type_dropdown],
        outputs=[metadata_output, status_output]
    )
    
    revise_btn.click(
        fn=revise_metadata,
        inputs=[input_text, metadata_output, revision_input, content_type_dropdown],
        outputs=[metadata_output, status_output]
    )
    
    download_btn.click(
        fn=save_json,
        inputs=[metadata_output],
        outputs=[download_file]
    ).then(
        lambda: gr.File(visible=True),
        outputs=[download_file]
    )
    
    # Custom CSS for compact layout
    demo.css = """
    #input_box, #metadata_box {
        height: 200px !important;
        min-height: 200px !important;
    }
    #status {
        padding: 10px;
        background: #f0f0f0;
        border-radius: 5px;
        margin: 10px 0;
    }
    """


if __name__ == "__main__":
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False
    )
