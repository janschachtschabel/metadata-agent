"""Validate schema JSON syntax with detailed error reporting."""
import json
import os
import glob

# Automatisch alle .json Dateien im schemata Ordner finden
schema_dir = "schemata"
schema_files = glob.glob(os.path.join(schema_dir, "*.json"))
schemas = [os.path.basename(f) for f in schema_files if not f.endswith(('.old', '.bak', '.backup', '.before_fix', '.broken', '.truncated', '.ctrl_bak'))]
schemas.sort()

print("=" * 80)
print("🔍 DETAILLIERTE SCHEMA-VALIDIERUNG")
print("=" * 80)
print(f"Gefundene Schema-Dateien: {len(schemas)}")
print()

errors = []

for schema_file in schemas:
    path = os.path.join(schema_dir, schema_file)
    print(f"\n📄 {schema_file}")
    print("-" * 80)
    
    if not os.path.exists(path):
        print("   ❌ Datei nicht gefunden!")
        errors.append((schema_file, "Datei nicht gefunden"))
        continue
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            data = json.loads(content)
        
        # Basic structure check
        profile_id = data.get("profileId", "❌ FEHLT")
        version = data.get("version", "❌ FEHLT")
        fields = data.get("fields", [])
        
        print(f"   ✅ JSON-Syntax: Valide")
        print(f"   📋 profileId: {profile_id}")
        print(f"   📌 version: {version}")
        print(f"   🔢 Felder: {len(fields)}")
        
        # Check fields structure
        if fields:
            required_count = sum(1 for f in fields if f.get("system", {}).get("required", False))
            print(f"   ⚠️  Pflichtfelder: {required_count}")
        
    except json.JSONDecodeError as e:
        print(f"   ❌ JSON-FEHLER:")
        print(f"      Zeile: {e.lineno}")
        print(f"      Spalte: {e.colno}")
        print(f"      Nachricht: {e.msg}")
        print(f"      Position: {e.pos}")
        
        # Show context
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if e.lineno <= len(lines):
                print(f"\n      Kontext (Zeile {e.lineno}):")
                start = max(0, e.lineno - 3)
                end = min(len(lines), e.lineno + 2)
                for i in range(start, end):
                    marker = " >>> " if i == e.lineno - 1 else "     "
                    print(f"{marker}{i+1:4d}: {lines[i].rstrip()}")
        
        errors.append((schema_file, f"Zeile {e.lineno}, Spalte {e.colno}: {e.msg}"))
    
    except Exception as e:
        print(f"   ❌ FEHLER: {str(e)}")
        errors.append((schema_file, str(e)))

print()
print("=" * 80)
print("📊 ZUSAMMENFASSUNG")
print("=" * 80)

if errors:
    print(f"\n❌ {len(errors)} Datei(en) mit Fehlern:\n")
    for file, error in errors:
        print(f"   • {file}: {error}")
    print()
else:
    print("\n✅ Alle Schema-Dateien sind valide!\n")

print("=" * 80)
