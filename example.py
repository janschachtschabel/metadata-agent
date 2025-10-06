"""Example script demonstrating metadata extraction without UI."""
import os
import json
from dotenv import load_dotenv
from agent import MetadataAgent
from models import WorkflowState
from schema_loader import SchemaManager
from validator import MetadataValidator

# Load environment
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    print("❌ OPENAI_API_KEY not found. Please set it in .env file.")
    exit(1)


def run_example():
    """Run a simple example extraction."""
    
    print("=" * 60)
    print("🤖 Metadaten-Extraktion Beispiel")
    print("=" * 60)
    print()
    
    # Initialize
    agent = MetadataAgent(api_key=API_KEY, model="gpt-5-mini")
    schema_manager = SchemaManager()
    validator = MetadataValidator()
    
    # Create initial state
    state = WorkflowState()
    
    # Example user input
    user_text = """
    Ich möchte eine Online-Konferenz dokumentieren:
    
    Titel: "Zukunft der Hochschullehre 2026"
    
    Die Konferenz behandelt den Einsatz von Künstlicher Intelligenz in der 
    Hochschuldidaktik und findet am 15. September 2026 statt. Sie richtet sich 
    an Lehrende und Forschende im Bereich digitale Bildung.
    
    Keywords: KI, Hochschuldidaktik, Digitale Lehre, Online-Veranstaltung
    
    Die Veranstaltung ist kostenlos und wird auf Deutsch durchgeführt.
    Website: https://konferenz2026.beispiel.de
    """
    
    print("📝 Eingabetext:")
    print(user_text)
    print()
    print("-" * 60)
    print()
    
    # Step 1: Initialize
    print("⚙️  Schritt 1: Initialisierung...")
    state = agent._init_node(state)
    print(f"   Geladenes Schema: {state.core_schema}")
    print(f"   Anzahl Felder: {len(state.field_status)}")
    print()
    
    # Step 2: Detect content type and suggest schema
    print("🔍 Schritt 2: Inhaltsart erkennen...")
    state.add_message("user", user_text)
    state = agent._suggest_special_schemas_node(state)
    
    if state.selected_content_types:
        print(f"   Erkannte Inhaltsart(en): {', '.join(state.selected_content_types)}")
        print(f"   Spezial-Schemata: {', '.join(state.special_schemas)}")
    else:
        print("   Keine spezifische Inhaltsart erkannt.")
    
    # Confirm special schema
    state.special_schema_confirmed = True
    print()
    
    # Step 3: Extract core required fields
    print("📋 Schritt 3: Pflichtfelder extrahieren...")
    state = agent._extract_core_required_node(state)
    
    required_fields = ["cclom:title", "cclom:general_description", "cclom:general_keyword"]
    for field_id in required_fields:
        status = state.field_status.get(field_id)
        if status and status.is_filled:
            value = status.value
            if isinstance(value, list):
                value = ", ".join(value)
            print(f"   ✅ {status.field_label}: {value[:80]}...")
        else:
            print(f"   ❌ {field_id}: Nicht extrahiert")
    
    state.core_required_complete = True
    print()
    
    # Step 4: Extract core optional fields
    print("📝 Schritt 4: Optionale Felder extrahieren...")
    state = agent._extract_core_optional_node(state)
    
    optional_extracted = []
    for field_id, status in state.field_status.items():
        if field_id not in required_fields and status.is_filled:
            value = status.value
            if isinstance(value, list):
                value = ", ".join(str(v) for v in value)
            optional_extracted.append(f"   • {status.field_label}: {value}")
    
    if optional_extracted:
        for line in optional_extracted[:5]:  # Show max 5
            print(line)
    else:
        print("   Keine optionalen Felder extrahiert")
    
    state.core_optional_complete = True
    print()
    
    # Step 5: Extract special schema fields
    if state.special_schemas:
        print("🎯 Schritt 5: Spezialfelder extrahieren...")
        state = agent._extract_special_schema_node(state)
        
        # Check for event-specific fields
        event_fields = ["schema:startDate", "schema:endDate", "oeh:eventType"]
        for field_id in event_fields:
            status = state.field_status.get(field_id)
            if status and status.is_filled:
                value = status.value
                if isinstance(value, list):
                    value = ", ".join(str(v) for v in value[:3])
                print(f"   • {status.field_label}: {value}")
        
        state.special_schema_complete = True
        print()
    
    # Step 6: Validate and normalize
    print("✅ Schritt 6: Validierung & Normalisierung...")
    
    # Get all fields
    all_fields = schema_manager.get_fields("core.json")
    if state.special_schemas:
        for schema_file in state.special_schemas:
            try:
                all_fields.extend(schema_manager.get_fields(schema_file))
            except:
                pass
    
    # Validate
    errors = validator.validate_metadata(state.metadata, all_fields)
    if errors:
        print("   ⚠️  Validierungsfehler:")
        for field_id, error in errors.items():
            print(f"      - {field_id}: {error}")
    else:
        print("   ✅ Alle Felder validiert")
    
    # Normalize
    normalized = validator.normalize_metadata(state.metadata, all_fields)
    print()
    
    # Step 7: Review
    print("📊 Schritt 7: Finale Metadaten")
    state = agent._review_node(state)
    print()
    
    # Output final JSON
    print("=" * 60)
    print("📄 Finales JSON:")
    print("=" * 60)
    
    # Filter empty values
    final_output = {k: v for k, v in state.metadata.items() if v and v != [] and v != ""}
    
    print(json.dumps(final_output, ensure_ascii=False, indent=2))
    print()
    
    # Statistics
    print("=" * 60)
    print("📈 Statistiken:")
    print("=" * 60)
    print(f"Gesamt Felder definiert: {len(state.field_status)}")
    print(f"Befüllte Felder: {sum(1 for s in state.field_status.values() if s.is_filled)}")
    print(f"Pflichtfelder: {sum(1 for s in state.field_status.values() if s.is_required)}")
    print(f"KI-vorgeschlagene Felder: {sum(1 for s in state.field_status.values() if s.ai_suggested)}")
    print()
    
    print("✅ Beispiel abgeschlossen!")
    print()
    print("💡 Tipp: Starte die Gradio UI mit 'python app.py' für eine interaktive Nutzung.")


if __name__ == "__main__":
    try:
        run_example()
    except Exception as e:
        print(f"❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
