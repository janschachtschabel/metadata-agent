"""Test script to verify validator integration."""
import os
from dotenv import load_dotenv
from agent import MetadataAgent
from schema_loader import SchemaManager, Field
from models import WorkflowState

load_dotenv()

def test_validator_normalization():
    """Test if validator normalizes values correctly."""
    print("=" * 60)
    print("🧪 Test 1: Validierung & Normalisierung")
    print("=" * 60)
    
    agent = MetadataAgent(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-5-mini")
    schema_manager = SchemaManager()
    
    # Get a field with normalization rules
    fields = schema_manager.get_fields("core.json")
    
    # Test data with whitespace and formatting issues
    test_data = {
        "cclom:title": "  Test Titel mit    mehreren   Spaces  ",
        "cclom:general_keyword": ["  Python  ", "Programmierung  ", "  Tutorial  "]
    }
    
    print(f"\n📥 Input (vor Normalisierung):")
    print(f"   Titel: '{test_data['cclom:title']}'")
    print(f"   Keywords: {test_data['cclom:general_keyword']}")
    
    # Apply validation
    normalized, warnings = agent._validate_and_normalize_fields(test_data, fields)
    
    print(f"\n📤 Output (nach Normalisierung):")
    print(f"   Titel: '{normalized.get('cclom:title', 'N/A')}'")
    print(f"   Keywords: {normalized.get('cclom:general_keyword', [])}")
    
    if warnings:
        print(f"\n⚠️  Warnungen:")
        for w in warnings:
            print(f"   {w}")
    else:
        print(f"\n✅ Keine Warnungen")
    
    # Check if normalization worked
    title_normalized = normalized.get("cclom:title", "").strip()
    keywords_normalized = normalized.get("cclom:general_keyword", [])
    
    success = True
    if "   " in title_normalized:  # Multiple spaces should be collapsed
        print("\n❌ Titel: Mehrfach-Leerzeichen nicht entfernt")
        success = False
    else:
        print("\n✅ Titel: Whitespace normalisiert")
    
    if any(k.startswith(" ") or k.endswith(" ") for k in keywords_normalized):
        print("❌ Keywords: Whitespace nicht getrimmt")
        success = False
    else:
        print("✅ Keywords: Whitespace getrimmt")
    
    return success


def test_vocabulary_validation():
    """Test vocabulary validation for closed vocabularies."""
    print("\n" + "=" * 60)
    print("🧪 Test 2: Vocabulary-Validierung")
    print("=" * 60)
    
    agent = MetadataAgent(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-5-mini")
    schema_manager = SchemaManager()
    
    # Get fields with vocabularies
    fields = schema_manager.get_fields("core.json")
    
    # Find a field with closed vocabulary
    vocab_field = None
    for field in fields:
        if field.vocabulary and field.vocabulary.get("type") == "closed":
            vocab_field = field
            break
    
    if not vocab_field:
        print("\n⏭️  Übersprungen: Kein Feld mit closed vocabulary in core.json gefunden")
        return True
    
    print(f"\n📋 Teste Feld: {vocab_field.prompt.get('label', vocab_field.id)}")
    print(f"   Vocabulary: {vocab_field.vocabulary.get('source', 'N/A')}")
    
    # Get allowed values
    concepts = vocab_field.get_vocabulary_concepts()
    if concepts:
        allowed = [c.get("label", "") for c in concepts[:3]]
        print(f"   Erlaubte Werte (Beispiele): {', '.join(allowed)}")
        
        # Test with invalid value
        test_data = {
            vocab_field.id: "UNGÜLTIGER_WERT_123"
        }
        
        print(f"\n📥 Input: {test_data}")
        normalized, warnings = agent._validate_and_normalize_fields(test_data, [vocab_field])
        
        print(f"📤 Output: {normalized}")
        
        if warnings:
            print(f"\n⚠️  Warnungen ({len(warnings)}):")
            for w in warnings:
                print(f"   {w}")
            print("\n✅ Validierung erkennt ungültige Werte")
            return True
        else:
            print("\n⚠️  Keine Warnung bei ungültigem Wert")
            return False
    else:
        print("\n⏭️  Übersprungen: Keine Konzepte gefunden")
        return True


def test_datatype_validation():
    """Test datatype validation."""
    print("\n" + "=" * 60)
    print("🧪 Test 3: Datentyp-Validierung")
    print("=" * 60)
    
    agent = MetadataAgent(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-5-mini")
    schema_manager = SchemaManager()
    
    fields = schema_manager.get_fields("core.json")
    
    # Find a date field
    date_field = None
    for field in fields:
        if field.datatype == "date":
            date_field = field
            break
    
    if not date_field:
        print("\n⏭️  Übersprungen: Kein Datumsfeld gefunden")
        return True
    
    print(f"\n📋 Teste Feld: {date_field.prompt.get('label', date_field.id)}")
    print(f"   Erwarteter Typ: date (YYYY-MM-DD)")
    
    # Test with invalid date format
    test_cases = [
        ("2025-10-07", True, "Gültiges Datum"),
        ("07.10.2025", False, "Ungültiges Format (DD.MM.YYYY)"),
        ("2025/10/07", False, "Ungültiges Format (YYYY/MM/DD)")
    ]
    
    all_passed = True
    for value, should_pass, description in test_cases:
        test_data = {date_field.id: value}
        normalized, warnings = agent._validate_and_normalize_fields(test_data, [date_field])
        
        has_warnings = len(warnings) > 0
        passed = has_warnings != should_pass  # Warning expected if should_pass=False
        
        status = "✅" if passed else "❌"
        print(f"\n{status} {description}: '{value}'")
        if warnings:
            print(f"   Warnung: {warnings[0][:80]}...")
        
        all_passed = all_passed and passed
    
    return all_passed


def test_end_to_end_extraction():
    """Test full extraction with validation."""
    print("\n" + "=" * 60)
    print("🧪 Test 4: End-to-End Extraktion mit Validierung")
    print("=" * 60)
    
    try:
        agent = MetadataAgent(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-5-mini")
        state = WorkflowState()
        
        # Initialize
        state = agent._init_node(state)
        print("\n✅ Agent initialisiert")
        
        # Add user input
        state.add_message("user", "Ein Python-Programmier Kurs für Anfänger über Grundlagen der Programmierung")
        
        # Extract core required fields
        print("\n🔍 Extrahiere Core-Pflichtfelder...")
        state = agent._extract_core_required_node(state)
        
        # Check if fields were extracted
        filled_fields = [f for f in state.field_status.values() if f.is_filled]
        print(f"   {len(filled_fields)} Felder extrahiert")
        
        # Show some extracted values
        for field_status in filled_fields[:3]:
            value_str = str(field_status.value)
            if len(value_str) > 50:
                value_str = value_str[:50] + "..."
            print(f"   ✅ {field_status.field_label}: {value_str}")
        
        if len(filled_fields) > 0:
            print("\n✅ Extraktion mit Validierung funktioniert")
            return True
        else:
            print("\n❌ Keine Felder extrahiert")
            return False
            
    except Exception as e:
        print(f"\n❌ Fehler: {str(e)}")
        return False


def main():
    """Run all validator tests."""
    print("\n" + "=" * 60)
    print("🧪 VALIDATOR INTEGRATION TESTS")
    print("=" * 60)
    
    results = []
    
    results.append(("Normalisierung", test_validator_normalization()))
    results.append(("Vocabulary-Validierung", test_vocabulary_validation()))
    results.append(("Datentyp-Validierung", test_datatype_validation()))
    results.append(("End-to-End Extraktion", test_end_to_end_extraction()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST ZUSAMMENFASSUNG")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} {test_name}")
    
    print("\n" + "-" * 60)
    print(f"Ergebnis: {passed}/{total} Tests bestanden")
    
    if passed == total:
        print("\n🎉 Alle Tests bestanden! Validator funktioniert korrekt.")
    else:
        print("\n⚠️  Einige Tests fehlgeschlagen. Bitte prüfen.")
    
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
