"""Minimales Beispiel: Automatische Metadatenextraktion ohne Chat-UI."""
import os
import json
from dotenv import load_dotenv
from agent import MetadataAgent
from models import WorkflowState

# Load environment
# Load all configuration from .env
load_dotenv()

# Beispieltext
TEXT = """Die Tagung Zukunft der Hochschullehre findet vom 15. bis 16. September 2026 an der Universität Potsdam statt. Im Mittelpunkt stehen innovative Lehrformate, digitale Prüfungen und KI-gestützte Lernumgebungen.
Die Veranstaltung richtet sich an Lehrende, Studiengangsverantwortliche und Hochschuldidaktiker:innen.
Neben Fachvorträgen von Expert:innen aus Deutschland und Österreich gibt es praxisorientierte Workshops und eine Poster-Session.
Veranstalter ist das Zentrum für Qualitätsentwicklung in Lehre und Studium (ZfQ).
Die Teilnahme kostet 120 €, ermäßigt 60 € für Studierende. Eine Anmeldung ist bis 20. August über die Website der Universität möglich.
Für Interessierte, die nicht vor Ort sein können, werden ausgewählte Programmpunkte live gestreamt."""

def main():
    print("=" * 70)
    print("🤖 AUTOMATISCHE METADATENEXTRAKTION (ohne Chat)")
    print("=" * 70)
    print()
    
    # Initialize Agent
    # ⚡ Alle Einstellungen werden aus .env geladen (OPENAI_API_KEY, OPENAI_MODEL, etc.)
    agent = MetadataAgent()
    state = WorkflowState()
    
    print("📝 Eingabetext:")
    print("-" * 70)
    print(TEXT)
    print("-" * 70)
    print()
    
    # Add user input to state
    state.add_message("user", TEXT)
    
    # === PHASE 1: INIT ===
    print("⚙️  Phase 1: Initialisierung...")
    state = agent._init_node(state)
    print(f"✅ Core-Schema geladen: {len(state.field_status)} Felder\n")
    
    # === PHASE 2: CORE REQUIRED ===
    print("📋 Phase 2: Core-Pflichtfelder extrahieren...")
    state = agent._extract_core_required_node(state)
    
    # Show extracted required fields
    for field_id in ["cclom:title", "cclom:general_description", "cclom:general_keyword"]:
        status = state.field_status.get(field_id)
        if status and status.is_filled:
            value = status.value
            if isinstance(value, list):
                value = ", ".join(str(v) for v in value[:3])
            else:
                value = str(value)[:60]
            print(f"   ✅ {status.field_label}: {value}...")
    
    state.core_required_complete = True
    print()
    
    # === PHASE 3: CORE OPTIONAL ===
    print("📋 Phase 3: Core-Optionale Felder extrahieren...")
    state = agent._extract_core_optional_node(state)
    
    # Show some optional fields
    optional_filled = [f for f in state.field_status.values() 
                      if f.is_filled and not f.is_required]
    print(f"   ✅ {len(optional_filled)} optionale Felder extrahiert")
    for field in optional_filled[:3]:
        value = str(field.value)[:50]
        print(f"      • {field.field_label}: {value}...")
    
    state.core_optional_complete = True
    print()
    
    # === PHASE 4: SPECIAL SCHEMA DETECTION ===
    print("🔍 Phase 4: Spezial-Schema erkennen...")
    state = agent._suggest_special_schemas_node(state)
    
    # ⚠️ WICHTIG: Nur das ERSTE erkannte Schema verwenden
    if state.selected_content_types:
        # Limitiere auf 1 Schema (falls mehrere erkannt wurden)
        state.selected_content_types = state.selected_content_types[:1]
        state.special_schemas = state.special_schemas[:1]
        
        print(f"   ✅ Erkannt: {state.selected_content_types[0]}")
        print(f"   📋 Schema: {state.special_schemas[0]}")
        state.special_schema_confirmed = True
    else:
        print("   ⚠️  Kein Spezial-Schema erkannt")
        state.special_schema_confirmed = True
    print()
    
    # === PHASE 5: SPECIAL SCHEMA FIELDS ===
    if state.special_schemas:
        print("📋 Phase 5: Spezial-Schema Felder extrahieren...")
        
        # 5a: Special Required
        state = agent._extract_special_required_node(state)
        special_required = [f for f in state.field_status.values() 
                           if f.is_filled and f.is_required and 
                           not f.field_id.startswith("cclom:")]
        
        if special_required:
            print(f"   ✅ {len(special_required)} Pflichtfelder:")
            for field in special_required:
                value = str(field.value)[:50]
                print(f"      • {field.field_label}: {value}...")
        
        state.special_required_complete = True
        
        # 5b: Special Optional
        state = agent._extract_special_optional_node(state)
        special_optional = [f for f in state.field_status.values() 
                           if f.is_filled and not f.is_required and 
                           not f.field_id.startswith("cclom:")]
        
        if special_optional:
            print(f"   ✅ {len(special_optional)} optionale Felder:")
            for field in special_optional[:3]:
                value = str(field.value)[:50]
                print(f"      • {field.field_label}: {value}...")
        
        state.special_optional_complete = True
        print()
    
    # === PHASE 6: REVIEW ===
    print("✅ Phase 6: Finalisierung...")
    state = agent._review_node(state)
    
    # Count total fields
    total_filled = len([f for f in state.field_status.values() if f.is_filled])
    total_confirmed = len([f for f in state.field_status.values() if f.is_confirmed])
    
    print(f"   📊 Gesamt: {total_filled} Felder extrahiert, {total_confirmed} bestätigt")
    print()
    
    # === EXPORT JSON ===
    print("=" * 70)
    print("📄 FINALE METADATEN (JSON)")
    print("=" * 70)
    
    # Filter out empty values
    final_metadata = {
        k: v for k, v in state.metadata.items()
        if v is not None and v != "" and v != [] and not k.startswith("_")
    }
    
    print(json.dumps(final_metadata, ensure_ascii=False, indent=2))
    print()
    
    # Save to file
    output_file = "extracted_metadata.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(final_metadata, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Metadaten gespeichert in: {output_file}")
    print()
    print("=" * 70)
    print("🎉 EXTRAKTION ABGESCHLOSSEN")
    print("=" * 70)


if __name__ == "__main__":
    main()
