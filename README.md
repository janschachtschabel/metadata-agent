# 🤖 Metadaten-Extraktion Agent

Ein intelligenter Agent zur automatischen Extraktion von Metadaten aus Textbeschreibungen, basierend auf konfigurierbaren JSON-Schemata.

## 🎯 Funktionen

- **KI-gestützte Extraktion**: Verwendet OpenAI GPT-5-mini zur intelligenten Metadatenextraktion
- **Dialogbasierter Workflow**: Geführte Konversation mit dem Nutzer über Gradio UI
- **Schema-basiert**: Flexible, erweiterbare JSON-Schemata für verschiedene Inhaltstypen
- **GPT-5 Reasoning**: Nutzt minimal reasoning für schnelle, präzise Extraktion
- **Mehrstufiger Prozess**:
  1. **Core-Pflichtfelder**: Titel, Beschreibung, Keywords (automatisch)
  2. **Core-Optional**: Autor, Lizenz, Sprache, etc. (ergänzbar)
  3. **Spezial-Schema-Erkennung**: KI schlägt passende Inhaltsart vor
  4. **Spezial-Felder**: Pro Schema Required + Optional nacheinander
- **Interaktive Korrekturen**: Jederzeit Felder korrigieren und neu bestätigen
- **Zurück-Navigation**: Mit "zurück" zu vorherigen Schritten springen
- **Mehrere Spezial-Schemas**: Nacheinander mehrere Typen bearbeiten
- **Validierung**: Pydantic-basierte Typenprüfung und Datenvalidierung
- **Langgraph Workflow**: Strukturierte Zustandsverwaltung und Gesprächsführung

## 🏗️ Architektur

```
┌─────────────────┐
│   Gradio UI     │  ← Benutzeroberfläche (Chat + Ergebnisse)
└────────┬────────┘
         │
┌────────▼────────┐
│  MetadataAgent  │  ← Langgraph Workflow Management
└────────┬────────┘
         │
┌────────▼────────┐
│  SchemaManager  │  ← Lädt und verwaltet JSON-Schemata
└────────┬────────┘
         │
┌────────▼────────┐
│  OpenAI LLM     │  ← GPT-5-mini mit Responses API
└─────────────────┘
```

## 📋 Voraussetzungen

- Python 3.10+
- OpenAI API Key

## 🚀 Installation

1. **Repository klonen oder Dateien herunterladen**

2. **Python Virtual Environment erstellen** (empfohlen):
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Abhängigkeiten installieren**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Umgebungsvariablen konfigurieren**:
   - Kopiere `.env.example` zu `.env`:
     ```bash
     copy .env.example .env
     ```
   - Füge deinen OpenAI API Key in `.env` ein:
     ```
     OPENAI_API_KEY=sk-...
     ```

## 🎮 Nutzung

### Starten der Anwendung

```bash
python app.py
```

Die Anwendung startet auf: `http://127.0.0.1:7860`

### Workflow

1. **Initialisierung**
   - Agent begrüßt dich und lädt das Core Schema (core.json)
   - Beschreibe die Ressource, die du dokumentieren möchtest

2. **Core-Pflichtfelder extrahieren** (aus core.json)
   - Titel (`cclom:title`)
   - Beschreibung (`cclom:general_description`)
   - Keywords (`cclom:general_keyword`)
   - Agent extrahiert automatisch aus deiner Beschreibung
   - Zeigt ✅ für gefundene und ❌ für fehlende Felder
   - **Korrigieren**: Gib neue Werte ein → Agent aktualisiert und zeigt erneut
   - **Bestätigen**: Schreibe "ok" oder "weiter" zum Fortfahren
   - **Zurück**: Schreibe "zurück" (falls verfügbar)

3. **Core-Optionale Felder** (aus core.json)
   - Agent zeigt automatisch extrahierte optionale Felder
   - Du kannst weitere Felder ergänzen:
     - Autor/in, Publisher, Lizenz, Sprache, etc.
   - **Korrigieren**: Gib neue Werte ein → Agent aktualisiert
   - **Fortfahren**: Schreibe "weiter"
   - **Zurück**: Schreibe "zurück" zu Pflichtfeldern

4. **Inhaltsart bestimmen**
   - Agent analysiert deine Beschreibung und schlägt eine Inhaltsart vor
   - Beispiel: "Veranstaltung", "Person", "Organisation"
   - **Automatisch erkannt**: Bestätige mit "ja" oder wähle "nein"
   - **Keine Erkennung**: Wähle per **Nummer** (z.B. "1") oder **Name** (z.B. "Event")
   - **Mehrfachauswahl**: "1,3" oder "Organisation, Person"
   - **Zurück**: Schreibe "zurück" zu optionalen Feldern

5. **Spezialschema-Felder** (z.B. aus event.json)
   - Falls bestätigt, werden typspezifische Felder **pro Schema** geladen
   - **Für jedes Schema:**
     - **a) Required-Felder**: Pflichtfelder für diesen Typ (z.B. Startdatum bei Events)
       - Korrigieren/Bestätigen wie bei Core-Feldern
     - **b) Optional-Felder**: Optionale typspezifische Felder
       - Ergänzen oder mit "weiter" fortfahren
   - **Mehrere Schemas**: Nacheinander durchlaufen (z.B. "Organisation (1/2)" → "Person (2/2)")
   - **Zurück-Navigation**: Zu vorigem Schema oder zu Schema-Auswahl

6. **Review & Export**
   - Finale JSON-Vorschau mit allen Feldern
   - Download der Metadaten als JSON
   - **Zurück**: Nochmal Felder korrigieren

### Beispiel-Konversation

```
User: Ich möchte eine Konferenz zum Thema KI in der Hochschullehre dokumentieren. 
      Der Titel ist "Zukunft der Hochschullehre 2026" und findet am 15. September 2026 statt.
      Sie richtet sich an Lehrende und behandelt digitale Lehrmethoden.

Agent: 📝 **Pflichtfelder (Core-Schema):**
       ✅ **Titel**: Zukunft der Hochschullehre 2026
       ✅ **Beschreibung**: Konferenz zum Thema KI in der Hochschullehre...
       ✅ **Keywords**: KI, Hochschullehre, Digitale Lehre
       
       ✅ Alle Pflichtfelder sind erfasst!

User: weiter

Agent: 📋 **Optionale Felder (Core-Schema):**
       ✅ **Zielgruppe**: Lehrende
       
       💡 Weitere wichtige optionale Felder:
       ⚪ **Sprache**: Sprachcode (z.B. "de", "en")
       ⚪ **Lizenz**: Lizenzangabe
       
       💬 Möchten Sie optionale Felder ergänzen oder korrigieren?
       Geben Sie die Werte ein oder 'weiter' zum Fortfahren.

User: Sprache: de

Agent: ✅ Sprache aktualisiert: de

User: weiter

Agent: 📋 Ich erkenne folgende Inhaltsart: **Veranstaltung**
       
       ❓ Soll ich das entsprechende Spezial-Schema laden? (ja/nein)

User: ja

Agent: ✅ Event-Schema geladen. Extrahiere Event-spezifische Felder...
       ✅ **Startdatum**: 2026-09-15
       
       ✅ Metadatenextraktion abgeschlossen!
```

## 📁 Projektstruktur & Dateien

### 🔧 **Kern-Dateien** (erforderlich)

| Datei | Beschreibung | Wichtigkeit |
|-------|--------------|-------------|
| **`app.py`** | Gradio UI - Hauptanwendung mit Chat, Zwischenergebnissen und JSON-Vorschau | ⭐⭐⭐ |
| **`agent.py`** | Langgraph Workflow Agent - Orchestriert alle Phasen, GPT-5 Integration, Feldextraktion | ⭐⭐⭐ |
| **`models.py`** | Pydantic Datenmodelle - WorkflowState, FieldStatus, Message, WorkflowPhase | ⭐⭐⭐ |
| **`schema_loader.py`** | Schema-Management - Lädt und parsed JSON-Schemata, verwaltet Felder | ⭐⭐⭐ |
| **`requirements.txt`** | Python Dependencies - Alle benötigten Pakete mit Versionen | ⭐⭐⭐ |

### 🗂️ **Schemata** (erforderlich)

| Datei | Beschreibung | Wichtigkeit |
|-------|--------------|-------------|
| **`schemata/core.json`** | Core-Schema - Basis-Metadaten (Titel, Beschreibung, Keywords, Lizenz, etc.) | ⭐⭐⭐ |
| **`schemata/event.json`** | Event-Schema - Veranstaltungsspezifische Felder (Datum, Ort, Typ) | ⭐⭐ |
| **`schemata/organization.json`** | Organisation-Schema - Name, Adresse, Kontakt | ⭐⭐ |
| **`schemata/person.json`** | Person-Schema - Name, Rolle, Affiliation | ⭐⭐ |

### 🛠️ **Hilfsdateien** (optional)

| Datei | Beschreibung | Löschen? |
|-------|--------------|----------|
| **`validator.py`** | Metadaten-Validierung & Normalisierung - Wird nur von example.py verwendet | ✅ Optional |
| **`example.py`** | CLI-Beispiel ohne UI - Nützlich zum Testen ohne Gradio | ✅ Optional |
| **`test_setup.py`** | Setup-Test-Script - Prüft Installation und Dependencies | ✅ Optional |
| **`start.bat`** | Windows Batch-Script - Startet App automatisch | ✅ Optional |

### 🗑️ **Überflüssige Dateien** (können gelöscht werden)

| Datei | Beschreibung | Löschen? |
|-------|--------------|----------|
| `agent.py.backup` | Alte Backup-Datei von agent.py | ✅ Ja |
| `fix_review.py` | Einmaliges Patch-Script (bereits angewendet) | ✅ Ja |
| `update_workflow.py` | Einmaliges Update-Script für Workflow-Migration | ✅ Ja |

### 📄 **Konfiguration**

| Datei | Beschreibung | Wichtigkeit |
|-------|--------------|-------------|
| **`.env`** | Umgebungsvariablen - Enthält OPENAI_API_KEY (nicht im Repo) | ⭐⭐⭐ |
| **`.env.example`** | Template für .env Datei | ⭐⭐ |
| **`.gitignore`** | Git Ignore Rules - Schützt .env und __pycache__ | ⭐⭐ |
| **`README.md`** | Diese Dokumentation | ⭐⭐ |

### 📚 **Dokumentation** (optional)

```
docs/
├── CHANGELOG.md          # Versionsänderungen
├── INSTALLATION.md       # Detaillierte Installationsanleitung
├── QUICKSTART.md         # 5-Minuten Schnellstart
└── PROJECT_SUMMARY.md    # Technische Projektübersicht
```

## 🔧 Konfiguration

### Schemata erweitern

Du kannst eigene Schemata in `schemata/` hinzufügen. Struktur:

```json
{
  "profileId": "type:mein-typ",
  "version": "1.0.0",
  "@context": { ... },
  "groups": [ ... ],
  "fields": [
    {
      "id": "mein:feld",
      "group": "basic",
      "group_label": "Basis",
      "prompt": {
        "label": "Feldname",
        "description": "Beschreibung für LLM und UI"
      },
      "system": {
        "path": "mein:feld",
        "datatype": "string",
        "multiple": false,
        "required": true,
        "ask_user": true,
        "ai_fillable": true,
        "normalization": { "trim": true }
      }
    }
  ],
  "output_template": {
    "mein:feld": ""
  }
}
```

### LLM-Modell ändern

In `app.py`, Zeile 18:

```python
agent = MetadataAgent(api_key=API_KEY, model="gpt-5")  # Oder "gpt-5-mini" (Standard), "gpt-5-nano"
```

## 📊 Datenfluss

```
User Input (Beschreibung)
    ↓
[Langgraph State Machine]
    ↓
Phase 1: Init
    ├─→ Load core.json schema
    ├─→ Initialize field status & phase history
    └─→ Welcome message
    ↓
Phase 2: Extract Core Required Fields
    ├─→ GPT-5 extracts from user text
    ├─→ Show ✅ filled / ❌ missing
    ├─→ Validate with Pydantic
    ├─→ User corrections → Re-show fields (loop)
    └─→ User confirms → Continue
    ↓
Phase 3: Extract Core Optional Fields
    ├─→ GPT-5 extracts optional fields
    ├─→ Show filled + important empty
    ├─→ User corrections → Re-show fields (loop)
    └─→ User says 'weiter' → Continue
    ↓
Phase 4: Suggest Special Schemas
    ├─→ GPT-5 detects content type(s)
    ├─→ Suggest matching schema(s)
    ├─→ User confirms (ja) / selects (1,3) / declines (nein)
    └─→ Load selected schema(s)
    ↓
Phase 5a: Extract Special Required (per schema)
    ├─→ Load CURRENT special schema (e.g. event.json 1/2)
    ├─→ GPT-5 extracts required fields
    ├─→ Show ✅ filled / ❌ missing
    ├─→ User corrections → Re-show (loop)
    └─→ User confirms → Continue to 5b
    ↓
Phase 5b: Extract Special Optional (per schema)
    ├─→ Show optional fields for CURRENT schema
    ├─→ User adds/corrects → Re-show (loop)
    ├─→ User says 'weiter'
    ├─→ IF more schemas → Jump back to 5a (next schema)
    └─→ ELSE → Continue to Review
    ↓
Phase 6: Review & Export
    ├─→ Compile final metadata from all schemas
    ├─→ Display JSON preview
    ├─→ Enable download
    └─→ User can still go back to correct
    
🔙 Zurück-Navigation verfügbar in allen Phasen (außer Init)
```

## ✨ Neue Features

### 🔄 **Interaktive Korrekturen**
- Jederzeit Felder korrigieren, ohne den Workflow neu zu starten
- Agent zeigt aktualisierte Werte sofort an
- **Kein automatisches Weiterspringen** nach Korrekturen
- Erst bei "ok" oder "weiter" geht es zur nächsten Phase

**Beispiel:**
```
Agent: ✅ Titel: Zertifikatskurs...
User: Der Titel ist "Digitale Medienbildung 2026"
Agent: ✅ Ich habe Ihre Änderungen verarbeitet. Hier die aktualisierten Daten:
       ✅ Titel: Digitale Medienbildung 2026
       💬 Bitte bestätigen Sie die Daten...
User: ok
```

### ⬅️ **Zurück-Navigation**
- Mit "zurück" zu jeder vorherigen Phase springen
- Agent zeigt nochmal alle Informationen der Phase
- Bei Spezial-Schemas: Zurück zum vorherigen Schema möglich

**Beispiel:**
```
User: zurück
Agent: ⬅️ Zurück zu: **Core-Pflichtfelder**
       📝 Pflichtfelder (Core-Schema):
       ✅ Titel: ...
       💬 Bitte bestätigen Sie die Daten...
```

### 📋 **Mehrere Spezial-Schemas nacheinander**
- Unterstützt mehrere Inhaltstypen gleichzeitig
- Jedes Schema wird einzeln durchlaufen (Required → Optional)
- Fortschrittsanzeige: "Organisation (1/2)", "Person (2/2)"

### 🔢 **Nummerierte Schema-Auswahl**
- Flexible Auswahl: Per Nummer ("1") oder Name ("Organisation")
- Mehrfachauswahl: "1,3" oder "Organisation, Person"
- KI schlägt automatisch passende Schemas vor

## 🧩 Module

### `schema_loader.py`
- `SchemaManager`: Lädt und cached JSON-Schemata
- `Field`: Repräsentiert ein Schema-Feld mit allen Metadaten
- Methoden: `get_fields()`, `get_required_fields()`, `get_optional_fields()`, `get_available_special_schemas()`

### `models.py`
- `WorkflowState`: Pydantic-Modell für Zustandsverwaltung
  - Verwaltet Felder, Messages, Completion-Flags
  - **Phase History**: Tracking für Zurück-Navigation (`phase_history`)
  - **Schema-Index**: Aktuelle Position bei mehreren Spezial-Schemas (`current_special_schema_index`)
- `WorkflowPhase`: Enum für Workflow-Phasen (7 Phasen: INIT → REVIEW)
- `FieldStatus`: Status eines einzelnen Feldes (gefüllt, bestätigt, KI-vorgeschlagen)
- `Message`: Chat-Nachricht (role, content, timestamp)

### `agent.py`
- `MetadataAgent`: Hauptagent mit Langgraph und GPT-5
- `_call_gpt5()`: GPT-5 Responses API Integration
- **Workflow-Nodes**: 
  - `_init_node()`: Initialisierung
  - `_extract_core_required_node()`: Core-Pflichtfelder
  - `_extract_core_optional_node()`: Core-Optionale Felder
  - `_suggest_special_schemas_node()`: Schema-Vorschlag & Auswahl
  - `_extract_special_required_node()`: Spezial-Pflichtfelder (pro Schema)
  - `_extract_special_optional_node()`: Spezial-Optionale Felder (pro Schema)
  - `_review_node()`: Finale Review & Export
- **User Input Processing**: `process_user_input()`
  - Erkennt Navigation-Befehle ("weiter", "ok", "zurück")
  - Verarbeitet Korrekturen und aktualisiert Felder
  - Verhindert Auto-Weiterleitung bei Korrekturen
- **LLM-Interaktion**: 
  - `_extract_fields()`: Extrahiert Feldwerte aus Text
  - `_detect_content_types()`: Erkennt Inhaltstypen für Schema-Vorschlag
- **Reasoning Control**: `default_reasoning_effort`, `default_verbosity`

### `app.py`
- Gradio UI mit 3 Bereichen:
  1. **Chat**: Konversation mit dem Agent
  2. **Zwischenergebnisse**: Extrahierte Daten (bestätigt vs. KI-Vorschlag)
  3. **JSON-Vorschau**: Finale Metadaten

## 🐛 Troubleshooting

### Fehler: "OPENAI_API_KEY not found"
- Stelle sicher, dass `.env` existiert und den Key enthält
- Format: `OPENAI_API_KEY=sk-...`

### Fehler: "Schema file not found"
- Überprüfe, dass alle referenzierten Schema-Dateien in `schemata/` existieren
- Core.json muss immer vorhanden sein

### LLM antwortet nicht korrekt
- Überprüfe API-Key und Kontingent auf https://platform.openai.com/usage
- Versuche ein anderes Modell (z.B. gpt-5 statt gpt-5-mini)
- Passe Reasoning Effort in `agent.py` (Zeile 30) an:
  - `minimal`: Sehr schnell (~0.5-1s), aktueller Standard
  - `low`: Etwas mehr Reasoning (~1-2s), bessere Qualität
  - `medium`: Ausgewogenes Reasoning (~2-3s), komplexe Texte
  - `high`: Maximale Qualität (~3-5s), schwierige Fälle

### Schema-Datei nicht gefunden
- Beispiel: "⚠️ Schema 'person.json' wurde nicht gefunden"
- Aktuell verfügbar: `event.json`
- Weitere Schemata müssen erstellt werden
- Oder: Entferne nicht-existierende Mappings aus `core.json`

## 🧹 Projekt bereinigen

Um das Projekt aufzuräumen, können folgende Dateien **sicher gelöscht** werden:

```powershell
# Definitiv löschen (einmalige Scripts & Backups):
rm agent.py.backup        # Alte Backup-Datei
rm fix_review.py          # Einmaliges Patch-Script  
rm update_workflow.py     # Einmaliges Update-Script

# Optional löschen (wenn nicht benötigt):
rm validator.py           # Nur für example.py verwendet
rm example.py             # CLI-Beispiel (optional für Tests)
rm test_setup.py          # Setup-Validierung (optional)
rm start.bat              # Windows-Startscript (Convenience)
```

**Minimale Kern-Installation** (nur erforderliche Dateien):
- `app.py`, `agent.py`, `models.py`, `schema_loader.py`
- `requirements.txt`, `.env` (erstellt), `.env.example`
- `schemata/*.json` (Core + Spezial-Schemas)
- `README.md`, `.gitignore`

## 🔮 Erweiterungsmöglichkeiten

- [ ] Session-Management für mehrere Nutzer
- [ ] Persistent Storage (DB statt in-memory)
- [ ] Batch-Verarbeitung mehrerer Ressourcen
- [ ] Export in verschiedene Formate (XML, RDF, Turtle)
- [ ] Validierung gegen externe Vocabularies (SKOS)
- [ ] Multi-Language Support
- [ ] Fine-tuned Model für Metadatenextraktion
- [ ] Integration mit externen Systemen (LMS, Repositories)
- [ ] Undo/Redo-Funktionalität
- [ ] Favoriten-Felder & Templates speichern

## 📝 Lizenz

Dieses Projekt ist ein Beispiel-/Mustercode für Bildungsmetadaten-Extraktion.

## 🤝 Beiträge

Feedback und Verbesserungsvorschläge sind willkommen!

## 📚 Verwendete Technologien

| Kategorie | Technologie | Version | Zweck |
|-----------|-------------|---------|-------|
| **LLM** | OpenAI | GPT-5-mini | Textanalyse & Extraktion |
| **API** | OpenAI Responses API | 1.30+ | GPT-5 Integration |
| **Workflow** | Langgraph | 0.0.20+ | State Machine |
| **UI** | Gradio | 4.16+ | Web-Interface |
| **Validierung** | Pydantic | 2.5+ | Typsicherheit |
| **Python** | 3.10+ | - | Runtime |

---

## 🆕 GPT-5 Features

### Reasoning Effort Control
```python
# In agent.py, Zeile 30-31:
self.default_reasoning_effort = "minimal"  # Fast extraction
self.default_verbosity = "low"  # Concise responses
```

**Reasoning Levels**:
- **minimal**: Sehr schnell (~0.5-1s), ideal für strukturierte Extraktion
- **low**: Etwas mehr Reasoning (~1-2s), bessere Qualität
- **medium**: Ausgewogenes Reasoning (~2-3s), komplexe Texte
- **high**: Maximale Qualität (~3-5s), schwierige Fälle

### Verbosity Control
```python
text={"verbosity": "low"}  # Kurze, präzise Antworten
```

**Verbosity Levels**:
- **low**: Kurze Antworten, weniger Tokens
- **medium**: Balanced
- **high**: Ausführliche Erklärungen

### Performance Benefits
- ⚡ **30-50% schneller** mit minimal reasoning
- 💰 **Ähnliche Kosten** durch effizienteres Token-Management
- 🎯 **Bessere Extraktion** durch Chain of Thought
- ✨ **Responses API** statt Chat Completions

---

## 📌 Version & Updates

**Aktuelle Version**: 2.0 (2025-10-06)

**Neueste Änderungen**:
- ✅ Mehrere Spezial-Schemas nacheinander verarbeiten
- ✅ Interaktive Korrekturen ohne Auto-Weiterleitung
- ✅ Zurück-Navigation zu allen vorherigen Phasen
- ✅ Nummerierte Schema-Auswahl (1,2,3 oder Namen)
- ✅ Flexible Mehrfachauswahl bei Inhaltstypen
- ✅ Phase-History für besseres Tracking
- ✅ Gradio Messages-Format (kein Deprecation Warning)

Siehe `docs/CHANGELOG.md` für vollständige Versionshistorie.

---

**Viel Erfolg beim Extrahieren von Metadaten! 🚀**
