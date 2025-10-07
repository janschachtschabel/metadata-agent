"""Gradio UI for metadata extraction agent."""
import gradio as gr
import json
import os
from dotenv import load_dotenv
from typing import List, Tuple, Dict
from agent import MetadataAgent
from models import WorkflowState, WorkflowPhase, Message

# Load environment variables
load_dotenv()

# Initialize agent (all settings from .env)
try:
    agent = MetadataAgent()
except ValueError as e:
    raise ValueError(f"Configuration error: {e}. Please check your .env file.")

# Global state (in production, use session management)
workflow_state = WorkflowState()


def initialize_workflow():
    """Initialize a new workflow (called on startup)."""
    global workflow_state
    workflow_state = WorkflowState()
    workflow_state = agent._init_node(workflow_state)
    return workflow_state


# Initialize workflow once at startup
workflow_state = initialize_workflow()


def format_chat_history(messages: List[Message]) -> List[Dict[str, str]]:
    """Format messages for Gradio chatbot display (messages format)."""
    chat_history = []
    
    for msg in messages:
        if msg.role in ["user", "assistant"]:
            chat_history.append({
                "role": msg.role,
                "content": msg.content
            })
    
    return chat_history


def format_intermediate_results(state: WorkflowState) -> str:
    """Format intermediate results as markdown."""
    if not state.field_status:
        return "*Noch keine Daten extrahiert*"
    
    sections = {}
    
    # Group by status
    for field_id, status in state.field_status.items():
        if not status.is_filled:
            continue
        
        group = "Bestätigt ✅" if status.is_confirmed else "KI-Vorschlag 🤖"
        if group not in sections:
            sections[group] = []
        
        value_str = status.value
        if isinstance(status.value, list):
            value_str = ", ".join(str(v) for v in status.value)
        
        sections[group].append(f"**{status.field_label}**: {value_str}")
    
    # Build markdown
    md = "## Extrahierte Metadaten\n\n"
    
    for section_name, items in sections.items():
        md += f"### {section_name}\n\n"
        md += "\n\n".join(items)
        md += "\n\n"
    
    # Add phase info
    phase_names = {
        WorkflowPhase.INIT: "Initialisierung",
        WorkflowPhase.SUGGEST_SPECIAL_SCHEMAS: "Spezialschema-Vorschlag",
        WorkflowPhase.EXTRACT_CORE_REQUIRED: "Pflichtfelder extrahieren",
        WorkflowPhase.EXTRACT_CORE_OPTIONAL: "Optionale Felder",
        WorkflowPhase.EXTRACT_SPECIAL_REQUIRED: "Spezial-Pflichtfelder",
        WorkflowPhase.EXTRACT_SPECIAL_OPTIONAL: "Spezial-Optionale Felder",
        WorkflowPhase.REVIEW: "Review",
        WorkflowPhase.COMPLETE: "Abgeschlossen ✅"
    }
    
    md += f"\n---\n**Status**: {phase_names.get(state.phase, state.phase)}\n"
    
    if state.selected_content_types:
        md += f"**Inhaltsart(en)**: {', '.join(state.selected_content_types)}\n"
    
    return md


def format_json_preview(state: WorkflowState) -> str:
    """Format JSON preview."""
    if not state.metadata:
        return "{}"
    
    # Filter out empty values for cleaner display
    filtered_metadata = {
        k: v for k, v in state.metadata.items()
        if v is not None and v != "" and v != []
    }
    
    return json.dumps(filtered_metadata, ensure_ascii=False, indent=2)


def chat_interaction(user_message: str, history: List[Tuple[str, str]]):
    """Handle chat interaction."""
    global workflow_state
    
    if not user_message.strip():
        return history, "", format_intermediate_results(workflow_state), format_json_preview(workflow_state)
    
    # Note: User message is added in process_user_input, so don't add it here
    
    # Process through workflow based on current phase (new workflow order)
    if workflow_state.phase == WorkflowPhase.INIT:
        # First user input: add message and extract core required fields
        workflow_state.add_message("user", user_message)
        # First user input: extract core required fields
        workflow_state = agent._extract_core_required_node(workflow_state)
        
    elif workflow_state.phase == WorkflowPhase.EXTRACT_CORE_REQUIRED:
        # User is confirming/correcting required fields
        workflow_state = agent.process_user_input(workflow_state, user_message)
        # Move to optional fields only if confirmed
        if workflow_state.core_required_complete:
            workflow_state = agent._extract_core_optional_node(workflow_state)
            
    elif workflow_state.phase == WorkflowPhase.EXTRACT_CORE_OPTIONAL:
        # User is adding optional fields or saying 'weiter'
        workflow_state = agent.process_user_input(workflow_state, user_message)
        # Move to suggest schemas if user said 'weiter'
        if workflow_state.core_optional_complete:
            workflow_state = agent._suggest_special_schemas_node(workflow_state)
            
    elif workflow_state.phase == WorkflowPhase.SUGGEST_SPECIAL_SCHEMAS:
        # User is confirming content type
        workflow_state = agent.process_user_input(workflow_state, user_message)
        # Move to special required if confirmed
        if workflow_state.special_schema_confirmed:
            workflow_state = agent._extract_special_required_node(workflow_state)
            
    elif workflow_state.phase == WorkflowPhase.EXTRACT_SPECIAL_REQUIRED:
        # User is confirming/correcting special required fields
        workflow_state = agent.process_user_input(workflow_state, user_message)
        # Move to special optional if confirmed
        if workflow_state.special_required_complete:
            workflow_state = agent._extract_special_optional_node(workflow_state)
            
    elif workflow_state.phase == WorkflowPhase.EXTRACT_SPECIAL_OPTIONAL:
        # User is adding special optional fields or saying 'weiter'
        workflow_state = agent.process_user_input(workflow_state, user_message)
        # Check if we need to process more schemas or go to review
        if workflow_state.special_optional_complete:
            # Check via routing function if more schemas
            route = agent._route_after_special_optional(workflow_state)
            if route == "next_schema":
                workflow_state = agent._extract_special_required_node(workflow_state)
            else:
                workflow_state = agent._review_node(workflow_state)
            
    elif workflow_state.phase == WorkflowPhase.REVIEW or workflow_state.phase == WorkflowPhase.COMPLETE:
        workflow_state.add_message("assistant", "Die Extraktion ist abgeschlossen. Sie können 'Neu starten' klicken für eine neue Extraktion.")
    
    # Format outputs
    chat_history = format_chat_history(workflow_state.messages)
    intermediate = format_intermediate_results(workflow_state)
    json_preview = format_json_preview(workflow_state)
    
    return chat_history, "", intermediate, json_preview


def reset_workflow():
    """Reset workflow to start fresh."""
    global workflow_state
    workflow_state = WorkflowState()
    workflow_state = agent._init_node(workflow_state)
    
    chat_history = format_chat_history(workflow_state.messages)
    intermediate = format_intermediate_results(workflow_state)
    json_preview = format_json_preview(workflow_state)
    
    return chat_history, "", intermediate, json_preview


def download_json(state_json: str):
    """Prepare JSON for download."""
    return state_json


# Build Gradio UI with custom CSS
custom_css = """
.gradio-container {
    font-size: 0.95rem;
}
.header-text h1 {
    margin-bottom: 0.5rem !important;
}
"""

with gr.Blocks(title="Metadaten-Extraktion Agent", theme=gr.themes.Soft(), css=custom_css) as demo:
    # Collapsible info section
    with gr.Accordion("ℹ️ Hilfe & Ablauf", open=False):
        gr.Markdown("""
        **Dieser Agent extrahiert strukturierte Metadaten aus Ihren Beschreibungen.**
        
        Verwendet: OpenAI GPT-5-mini + Langgraph
        
        ### 📝 Workflow:
        1. **Core-Pflichtfelder**: Titel, Beschreibung, Keywords (automatisch extrahiert)
        2. **Core-Optionale Felder**: Autor, Lizenz, Sprache, etc. (ergänzen oder überspringen)
        3. **Inhaltsart bestimmen**: Agent schlägt passende Kategorie vor (z.B. Veranstaltung)
        4. **Spezial-Schema**: Zusätzliche typspezifische Felder (z.B. Datum, Ort bei Events)
        5. **Review**: Finale JSON-Vorschau und Download
        
        💡 **Tipp**: Je detaillierter Ihre Beschreibung, desto besser die Extraktion!
        """)
    
    with gr.Row():
        # Left column: Chat
        with gr.Column(scale=2):
            gr.Markdown("## 🤖 Metadaten-Extraktions Chat")
            chatbot = gr.Chatbot(
                height=500,
                label="Konversation",
                show_label=False,
                avatar_images=("👤", "🤖"),  # User and AI avatars
                type="messages"  # Use new messages format
            )
            
            with gr.Row():
                user_input = gr.Textbox(
                    placeholder="Ihre Nachricht hier eingeben...",
                    show_label=False,
                    scale=4,
                    lines=2
                )
                send_btn = gr.Button("Senden", variant="primary", scale=1)
            
            with gr.Row():
                reset_btn = gr.Button("🔄 Neu starten", variant="secondary")
                clear_btn = gr.Button("🗑️ Chat löschen", variant="secondary")
    
        # Right column: Results
        with gr.Column(scale=1):
            intermediate_results = gr.Markdown(
                value="*Noch keine Daten extrahiert*",
                label="Extrahierte Daten"
            )
    
    # Bottom row: JSON Preview
    with gr.Row():
        with gr.Column():
            gr.Markdown("## 📄 JSON Vorschau")
            json_preview = gr.Code(
                value="{}",
                language="json",
                label="Metadaten JSON",
                lines=20
            )
            download_btn = gr.Button("💾 JSON herunterladen", variant="secondary")
            download_file = gr.File(label="Download", visible=False)
    
    # Event handlers
    def send_message(msg, history):
        return chat_interaction(msg, history)
    
    send_btn.click(
        fn=send_message,
        inputs=[user_input, chatbot],
        outputs=[chatbot, user_input, intermediate_results, json_preview]
    )
    
    user_input.submit(
        fn=send_message,
        inputs=[user_input, chatbot],
        outputs=[chatbot, user_input, intermediate_results, json_preview]
    )
    
    reset_btn.click(
        fn=reset_workflow,
        inputs=[],
        outputs=[chatbot, user_input, intermediate_results, json_preview]
    )
    
    clear_btn.click(
        fn=lambda: ([], ""),
        inputs=[],
        outputs=[chatbot, user_input]
    )
    
    download_btn.click(
        fn=lambda json_str: gr.File(value=None, visible=False),
        inputs=[json_preview],
        outputs=[download_file]
    )
    
    # Load initial state (already initialized at startup)
    def get_initial_state():
        """Get the initial state without re-initializing."""
        chat_history = format_chat_history(workflow_state.messages)
        intermediate = format_intermediate_results(workflow_state)
        json_preview_text = format_json_preview(workflow_state)
        return chat_history, "", intermediate, json_preview_text
    
    demo.load(
        fn=get_initial_state,
        inputs=[],
        outputs=[chatbot, user_input, intermediate_results, json_preview]
    )

if __name__ == "__main__":
    demo.launch(share=False, server_name="127.0.0.1", server_port=7860)
