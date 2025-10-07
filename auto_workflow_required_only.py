"""Ultra-schneller Workflow: Nur Pflichtfelder (Minimal-Modus)."""
import os
import json
from dotenv import load_dotenv
from agent import MetadataAgent
from models import WorkflowState

# Load all configuration from .env
load_dotenv()

TEXT = """Die Tagung Zukunft der Hochschullehre findet vom 15. bis 16. September 2026 an der Universität Potsdam statt."""

def main():
    print("=" * 70)
    print("🚀 ULTRA-SCHNELLER WORKFLOW (Nur Pflichtfelder)")
    print("=" * 70)
    print()
    
    # ⚡ ULTRA-PERFORMANCE: Nur Pflichtfelder für maximale Geschwindigkeit
    # Alle Einstellungen werden aus .env geladen
    agent = MetadataAgent()
    state = WorkflowState()
    state.add_message("user", TEXT)
    
    # Phase 1: Init
    print("⚙️  Initialisierung...")
    state = agent._init_node(state)
    
    # Phase 2: Nur Core Required (3 Felder)
    print("📋 Core-Pflichtfelder extrahieren...")
    state = agent._extract_core_required_node(state)
    state.core_required_complete = True
    
    # Skip Phase 3 (Core Optional)
    state.core_optional_complete = True
    
    # Phase 4: Schema Detection
    print("🔍 Spezial-Schema erkennen...")
    state = agent._suggest_special_schemas_node(state)
    if state.selected_content_types:
        state.selected_content_types = state.selected_content_types[:1]
        state.special_schemas = state.special_schemas[:1]
        print(f"   ✅ Erkannt: {state.selected_content_types[0]}")
        state.special_schema_confirmed = True
    else:
        state.special_schema_confirmed = True
    
    # Phase 5: Nur Special Required (keine Optional)
    if state.special_schemas:
        print("📋 Spezial-Pflichtfelder extrahieren...")
        state = agent._extract_special_required_node(state)
        state.special_required_complete = True
        state.special_optional_complete = True
    
    # Phase 6: Review
    state = agent._review_node(state)
    
    # Export
    final_metadata = {k: v for k, v in state.metadata.items() if v and not k.startswith("_")}
    
    print()
    print("=" * 70)
    print("📄 FINALE METADATEN")
    print("=" * 70)
    print(json.dumps(final_metadata, ensure_ascii=False, indent=2))
    
    print()
    print(f"✅ Fertig! {len([f for f in state.field_status.values() if f.is_filled])} Felder extrahiert")
    print("💡 Nur Pflichtfelder = Maximale Performance!")

if __name__ == "__main__":
    main()
