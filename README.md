# 🤖 Metadaten-Extraktion Agent

Ein intelligenter Agent zur automatischen Extraktion von Metadaten aus Textbeschreibungen, basierend auf konfigurierbaren JSON-Schemata.

## 📑 Inhaltsverzeichnis

- [🎯 Funktionen](#-funktionen)
- [🏗️ Architektur](#️-architektur)
- [📋 Voraussetzungen](#-voraussetzungen)
- [🚀 Installation](#-installation)
- [🎮 Workflow-Optionen](#-workflow-optionen)
  - [Option 1: Automatisch (ohne Mensch)](#option-1-automatisch-ohne-mensch)
  - [Option 2: Minimal-UI (mit Feedback)](#option-2-minimal-ui-mit-feedback)
  - [Option 3: Komplexer Chatbot](#option-3-komplexer-chatbot)
- [🎮 Detaillierte Nutzung](#-detaillierte-nutzung)
  - [Mit Chatbot (Gradio UI)](#starten-der-anwendung)
  - [Workflow-Beschreibung](#workflow)
  - [Beispiel-Konversation](#beispiel-konversation)
- [🔧 Code-Beispiele & Details](#-code-beispiele--details)
- [✅ Schema-Validierung](#-schema-validierung)
- [📁 Projektstruktur & Dateien](#-projektstruktur--dateien)
  - [Basis-Schema & Inhaltstypen](#️-schemata-erforderlich)
  - [11 JSON-Schemata](#basis-schema)
- [🔧 Konfiguration](#-konfiguration)
- [📊 Datenfluss](#-datenfluss)
- [✨ Neue Features](#-neue-features)
- [🧩 Module](#-module)
- [🐛 Troubleshooting](#-troubleshooting)
- [🔮 Erweiterungsmöglichkeiten](#-erweiterungsmöglichkeiten)

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
     # Windows
     copy .env.example .env
     
     # Linux/Mac
     cp .env.example .env
     ```
   - **Minimal:** Nur API Key eintragen (Rest ist optional):
     ```env
     OPENAI_API_KEY=sk-proj-xxxxx
     ```
   - **Mit GPT-5 (Standard):**
     ```env
     OPENAI_API_KEY=sk-proj-xxxxx
     OPENAI_MODEL=gpt-5-mini
     GPT5_REASONING_EFFORT=minimal  # Nur für GPT-5
     GPT5_VERBOSITY=low             # Nur für GPT-5
     ```
   - **Mit GPT-4o (Alternative):**
     ```env
     OPENAI_API_KEY=sk-proj-xxxxx
     OPENAI_MODEL=gpt-4o
     # GPT5_* Parameter werden automatisch ignoriert
     ```
   
   📚 **Vollständige Dokumentation:** Siehe [docs/CONFIGURATION.md](docs/CONFIGURATION.md)
   
   **Unterstützte Modelle:**
   - ✅ GPT-5 Familie: `gpt-5-mini`, `gpt-5-nano`, `gpt-5` (mit reasoning/verbosity)
   - ✅ GPT-4 Familie: `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo` (Standard API)
   - ✅ Andere: `gpt-3.5-turbo` oder kompatible Modelle

## 🎮 Workflow-Optionen

Es stehen **3 verschiedene Workflows** zur Verfügung - je nach Anwendungsfall:

---

### **Option 1: Automatisch (ohne Mensch)** 🤖

**Datei:** `auto_workflow_full.py` oder `auto_workflow_required_only.py`

**Start:**
```bash
# Vollständig (Pflicht + Optional)
python auto_workflow_full.py

# Nur Pflichtfelder (schneller)
python auto_workflow_required_only.py
```

**Eigenschaften:**
- ⚡ Durchläuft alle Schritte automatisch
- 📋 Keine Benutzerinteraktion erforderlich
- 🎯 Wahlweise Vollversion oder Minimal-Version (nur Pflichtfelder)
- ⏱️ **Dauer:** ~20 Sekunden (Full) / ~5-8 Sekunden (Required Only)
- 💾 Speichert JSON automatisch

**Anwendungsfall:** Batch-Verarbeitung, API-Integration, Automatisierung

---

### **Option 2: Minimal-UI (mit Feedback)** 📱

**Datei:** `app_minimal.py`

**Start:**
```bash
python app_minimal.py
```
**URL:** http://127.0.0.1:7860

**Eigenschaften:**
- 🎨 Kompakte UI für Seitenleisten (8 Zeilen Felder)
- 📝 **Eingabe:** Textfeld + Dropdown für Inhaltsart (Automatisch/Manuell)
- 📊 **Ausgabe:** JSON-Vorschau
- ✏️ **Änderungen:** Revision-Button mit Eingabefeld
- 🔄 Bei Änderungen: Kompletter Prozess wird erneut durchlaufen
  - **Vorteil:** Erneute Prüfung auf Vokabulare und Validierung
- ⏱️ **Dauer:** ~20 Sekunden pro Durchlauf
- 💾 JSON-Download-Button

**Anwendungsfall:** Schnelle Extraktion mit Korrekturmöglichkeit, Seitenleisten-Integration

---

### **Option 3: Komplexer Chatbot** 💬

**Datei:** `app.py`

**Start:**
```bash
python app.py
```
**URL:** http://127.0.0.1:7860

**Eigenschaften:**
- 🗣️ Geführte Abfrage in Schritten
- 📋 **UI-Elemente:**
  - Chatbereich für Dialog
  - Texteingabefeld
  - Auswahlfeld für Metadatenvorschau
  - Optionale JSON-Anzeige
- 📊 **Workflow-Schritte:**
  1. Core Pflichtmetadaten
  2. Core optionale Metadaten
  3. Inhaltsart für Schemata (KI-Vorschlag oder manuell)
  4. Spezial-Schemata Pflichtmetadaten
  5. Spezial-Schemata optionale Metadaten
- 💡 **Vorteile:**
  - User wird nicht überlastet (immer nur Teildaten)
  - Chatbot kann Rückfragen zum Vokabular beantworten
  - Gibt Hinweise auf weitere mögliche Felder
  - Korrekturen jederzeit möglich
- ⏱️ **Dauer:** ~20 Sekunden für Volldurchlauf
- 🖥️ Höherer Platzbedarf im UX

**Anwendungsfall:** Interaktive Erfassung mit Beratung, komplexe Metadaten, explorative Nutzung

---

### **Vergleichstabelle**

| Kriterium | Automatisch | Minimal-UI | Komplexer Chatbot |
|-----------|-------------|------------|-------------------|
| **Datei** | `auto_workflow_*.py` | `app_minimal.py` | `app.py` |
| **Port** | - | 7860 | 7860 |
| **Interaktion** | Keine | Minimal (Feedback) | Vollständig (Dialog) |
| **UI-Größe** | - | Klein (Sidebar) | Groß (Fullscreen) |
| **Schritte** | Alle automatisch | Auf einmal | Schrittweise |
| **Änderungen** | Nicht möglich | Re-Extraktion | Während Workflow |
| **Vokabular-Hilfe** | Automatisch | Automatisch | + Chat-Beratung |
| **Dauer** | 5-20s | ~20s | ~20s |
| **Best for** | Batch/API | Quick Edit | Komplexe Fälle |

---

## 🎮 Detaillierte Nutzung

### Starten der Anwendung

Siehe [Workflow-Optionen](#-workflow-optionen) für die verschiedenen Startmöglichkeiten

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

## 🔧 Code-Beispiele & Details

> 💡 **Für einen Überblick siehe:** [Workflow-Optionen](#-workflow-optionen)

---

### 💻 Code-Beispiel

Beide Scripts nutzen die gleiche Struktur:

```python
from dotenv import load_dotenv
from agent import MetadataAgent
from models import WorkflowState

# Alle Einstellungen aus .env laden
load_dotenv()

# Text definieren
TEXT = """Die Tagung Zukunft der Hochschullehre findet vom 15. bis 16. September 2026..."""

# Agent initialisieren (lädt Config aus .env)
agent = MetadataAgent()
state = WorkflowState()
state.add_message("user", TEXT)

# Workflow-Phasen durchlaufen
state = agent._init_node(state)                          # Phase 1: Init
state = agent._extract_core_required_node(state)         # Phase 2: Core Required
state.core_required_complete = True

# auto_workflow_full.py:    → Extrahiert Optional-Felder
# auto_workflow_required_only.py: → Überspringt Optional-Felder
state = agent._extract_core_optional_node(state)         # Phase 3: Core Optional
state.core_optional_complete = True

state = agent._suggest_special_schemas_node(state)       # Phase 4: Schema Detection
state.special_schema_confirmed = True

state = agent._extract_special_required_node(state)      # Phase 5a: Special Required
state.special_required_complete = True

state = agent._extract_special_optional_node(state)      # Phase 5b: Special Optional
state.special_optional_complete = True

state = agent._review_node(state)                        # Phase 6: Review

# Metadaten exportieren
final_metadata = {k: v for k, v in state.metadata.items() if v}
```

---

### 📊 Output-Beispiel (auto_workflow_full.py)

```
======================================================================
🤖 AUTOMATISCHE METADATENEXTRAKTION (Vollständig)
======================================================================

📝 Eingabetext:
----------------------------------------------------------------------
Die Tagung Zukunft der Hochschullehre findet vom 15. bis 16. September...
----------------------------------------------------------------------

⚙️  Phase 1: Initialisierung...
✅ Core-Schema geladen: 15 Felder

📋 Phase 2: Core-Pflichtfelder extrahieren...
   ✅ Titel: Zukunft der Hochschullehre
   ✅ Beschreibung: Die Tagung Zukunft der Hochschullehre findet...
   ✅ Keywords: Hochschullehre, digitale Prüfungen, KI

📋 Phase 3: Core-Optionale Felder extrahieren...
   ✅ 4 optionale Felder extrahiert
      • Zielgruppe: Lehrende, Studiengangsverantwortliche
      • Kosten: 120 € (ermäßigt 60 € für Studierende)
      • Sprache: de

🔍 Phase 4: Spezial-Schema erkennen...
   ✅ Erkannt: Veranstaltung
   📋 Schema: event.json

📋 Phase 5: Spezial-Schema Felder extrahieren...
   ✅ 3 Pflichtfelder:
      • Startdatum: 2026-09-15
      • Endedatum: 2026-09-16
      • Ort: Universität Potsdam
   ✅ 5 optionale Felder:
      • Veranstaltungsformat: Konferenz
      • Anmeldeschluss: 2026-08-20

✅ Phase 6: Finalisierung...
   📊 Gesamt: 23 Felder extrahiert

======================================================================
📄 FINALE METADATEN (JSON)
======================================================================
{
  "cclom:title": "Zukunft der Hochschullehre",
  "cclom:general_description": "Die Tagung...",
  "cclom:general_keyword": ["Hochschullehre", "digitale Prüfungen"],
  "schema:startDate": "2026-09-15",
  "schema:endDate": "2026-09-16",
  "schema:location": {
    "@type": "Place",
    "name": "Universität Potsdam"
  }
}

💾 Metadaten gespeichert in: extracted_metadata.json
```

---

## ✅ Schema-Validierung

### Validierung aller Schemata

Das Tool `validate_schemas.py` prüft **automatisch alle** JSON-Dateien im `schemata/` Ordner:

```bash
python validate_schemas.py
```

### Funktionsweise

```python
import glob
import json

# Findet automatisch alle .json Dateien
schema_files = glob.glob("schemata/*.json")
schemas = [os.path.basename(f) for f in schema_files 
           if not f.endswith(('.old', '.bak', '.backup'))]
schemas.sort()

for schema_file in schemas:
    try:
        with open(f"schemata/{schema_file}", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Validiere Struktur
        profile_id = data.get("profileId")
        fields = data.get("fields", [])
        required_fields = [f for f in fields if f.get("system", {}).get("required")]
        
        print(f"✅ {schema_file}")
        print(f"   profileId: {profile_id}")
        print(f"   Felder: {len(fields)}")
        print(f"   Pflichtfelder: {len(required_fields)}")
    except json.JSONDecodeError as e:
        print(f"❌ {schema_file}: Zeile {e.lineno}, {e.msg}")
```

### Output-Beispiel

```
===========================================================================
🔍 DETAILLIERTE SCHEMA-VALIDIERUNG
===========================================================================
Gefundene Schema-Dateien: 11

📄 core.json
---------------------------------------------------------------------------
   ✅ JSON-Syntax: Valide
   📋 profileId: core:descriptive
   📌 version: 1.7.0
   🔢 Felder: 15
   ⚠️  Pflichtfelder: 3

📄 person.json
---------------------------------------------------------------------------
   ✅ JSON-Syntax: Valide
   📋 profileId: core:person
   📌 version: 1.0.0
   🔢 Felder: 37
   ⚠️  Pflichtfelder: 3

📄 tool_service.json
---------------------------------------------------------------------------
   ✅ JSON-Syntax: Valide
   📋 profileId: core:tool_service
   📌 version: 1.0.0
   🔢 Felder: 28
   ⚠️  Pflichtfelder: 2

===========================================================================
📊 ZUSAMMENFASSUNG
===========================================================================
✅ Alle 11 Dateien sind valide!
```

### Validierungs-Features

| Feature | Beschreibung |
|---------|--------------|
| **Automatische Erkennung** | Findet alle `.json` Dateien in `schemata/` |
| **Syntax-Check** | Prüft JSON-Syntax und encoding |
| **Struktur-Validierung** | Prüft `profileId`, `version`, `fields` |
| **Pflichtfeld-Analyse** | Zählt required vs. optional Felder |
| **Fehlerdetails** | Zeigt exakte Zeile/Spalte bei Syntax-Fehlern |
| **Backup-Filterung** | Ignoriert `.old`, `.bak`, `.before_fix` Dateien |

### Integration in Validator

Der `validator.py` nutzt Pydantic für **Laufzeit-Validierung**:

```python
from validator import MetadataValidator

validator = MetadataValidator()

# Validiere Metadaten
metadata = {
    "cclom:title": "Mein Kurs",
    "cclom:general_keyword": ["Python", "AI"],
    "schema:startDate": "2026-09-15"
}

# Automatische Validierung
validated = validator.validate_metadata(metadata, schema_info)

# Fehler werden automatisch erkannt:
# - Falsche Datentypen (string statt date)
# - Fehlende Pflichtfelder
# - Ungültige Werte (z.B. Email-Format)
```

### Validierungs-Ebenen

| Ebene | Tool | Zeitpunkt | Zweck |
|-------|------|-----------|-------|
| **Schema-Syntax** | `validate_schemas.py` | Entwicklungszeit | JSON-Dateien prüfen |
| **Struktur** | `schema_loader.py` | Ladezeit | Schema-Format validieren |
| **Daten-Typ** | `validator.py` (Pydantic) | Laufzeit | Metadaten validieren |
| **Business-Logik** | `agent.py` | Extraktion | Feldabhängigkeiten prüfen |

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

#### **Basis-Schema**
| Datei | Beschreibung | Felder | Wichtigkeit |
|-------|--------------|--------|-------------|
| **`schemata/core.json`** | Core-Schema - Basis-Metadaten für alle Inhaltstypen (Titel, Beschreibung, Keywords, Lizenz, Autor, Sprache, etc.) | 15 | ⭐⭐⭐ |

#### **Inhaltstyp-Schemata**
| Datei | Beschreibung | Felder | Wichtigkeit |
|-------|--------------|--------|-------------|
| **`schemata/person.json`** | Person-Schema - Personen, Experten, Lehrende (Name, Email, Rolle, Affiliation, Expertise, Publikationen) | 37 | ⭐⭐ |
| **`schemata/source.json`** | Quelle/Kanal-Schema - Repositories, Portale, Datenbanken (Quellentyp, Harvesting, Vererbung, Governance) | 19 | ⭐⭐ |
| **`schemata/tool_service.json`** | Tool/Service-Schema - Software, Plattformen, Apps (Funktion, Zielgruppe, Technologie, Kosten, Barrierefreiheit) | 28 | ⭐⭐ |
| **`schemata/event.json`** | Event-Schema - Veranstaltungen, Konferenzen, Workshops (Datum, Ort, Typ, Veranstalter, Kosten) | 22 | ⭐⭐ |
| **`schemata/organization.json`** | Organisation-Schema - Institutionen, Bildungseinrichtungen (Name, Adresse, Kontakt, Typ) | 34 | ⭐⭐ |
| **`schemata/education_offer.json`** | Bildungsangebot-Schema - Kurse, Zertifikate, Studiengänge (Niveau, Dauer, Abschluss, Voraussetzungen) | 20 | ⭐⭐ |
| **`schemata/didactic_planning_tools.json`** | Didaktik-Tools-Schema - Planungs- und Unterrichtswerkzeuge (Didaktischer Ansatz, Einsatzszenario) | 24 | ⭐⭐ |
| **`schemata/prompt.json`** | Prompt-Schema - KI-Prompts für Bildungskontexte (Prompt-Text, Funktion, Szenario, Modelle) | JSON Schema | ⭐⭐ |

#### **Vokabulare (SKOS)**
| Datei | Beschreibung | Typ | Wichtigkeit |
|-------|--------------|-----|-------------|
| **`schemata/occupation.json`** | Berufe-Vokabular - Hierarchisches Vokabular mit ISCO/ESCO-Mappings (8 Top-Konzepte: Bildung, Gesundheit, Handwerk, IT, etc.) | SKOS ConceptScheme | ⭐⭐ |
| **`schemata/learning_materials.json`** | Lernmaterial-Vokabular - Taxonomie für Lernressourcen | SKOS ConceptScheme | ⭐⭐ |

### 🛠️ **Hilfsdateien** (optional)

| Datei | Beschreibung | Wichtigkeit |
|-------|--------------|-------------|
| **`validator.py`** | Metadaten-Validierung & Normalisierung - Pydantic-basierte Validierung mit Typenprüfung | ⭐⭐ |
| **`test_validator.py`** | Validator-Tests - Unit-Tests für Validierungslogik | ⭐ |
| **`validate_schemas.py`** | Schema-Validierung - Prüft alle JSON-Schemata auf Syntax-Fehler | ⭐⭐ |
| **`example_workflow_withoutchatbot.py`** | CLI-Beispiel - Automatische Extraktion ohne Chat-UI (siehe unten) | ⭐⭐ |

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

**Minimale Kern-Installation** - Diese Dateien werden benötigt:

### **Essenzielle Dateien** ⭐⭐⭐
```
app.py                              # Gradio UI (Chatbot-Modus)
agent.py                            # Workflow-Agent
models.py                           # Datenmodelle
schema_loader.py                    # Schema-Loader
requirements.txt                    # Dependencies
.env                                # API-Key (selbst erstellen)
.env.example                        # Template
README.md                           # Dokumentation
.gitignore                          # Git-Konfiguration
```

### **Schemata** ⭐⭐⭐
```
schemata/core.json                  # Pflicht: Basis-Schema
schemata/person.json                # Optional: Person-Schema
schemata/source.json                # Optional: Quelle-Schema
schemata/tool_service.json          # Optional: Tool-Schema
schemata/event.json                 # Optional: Event-Schema
schemata/organization.json          # Optional: Organisation-Schema
schemata/education_offer.json       # Optional: Bildungsangebot-Schema
schemata/didactic_planning_tools.json  # Optional: Didaktik-Tools-Schema
schemata/prompt.json                # Optional: Prompt-Schema
schemata/occupation.json            # Optional: Berufe-Vokabular
schemata/learning_materials.json    # Optional: Lernmaterial-Vokabular
```

### **Nützliche Hilfsdateien** ⭐⭐
```
validator.py                        # Validierung (empfohlen)
validate_schemas.py                 # Schema-Validierung (empfohlen)
example_workflow_withoutchatbot.py  # Batch-Verarbeitung (empfohlen)
test_validator.py                   # Tests (optional)
extracted_metadata.json             # Beispiel-Output (optional)
```

### **Dokumentation** ⭐
```
docs/CHANGELOG.md                   # Versionshistorie
docs/INSTALLATION.md                # Detaillierte Installation
docs/QUICKSTART.md                  # Schnellstart
docs/PROJECT_SUMMARY.md             # Technische Übersicht
docs/VALIDATION.md                  # Validierungs-Dokumentation
```

### **Löschbare Dateien** ❌

Alle temporären Check- und Fix-Scripts wurden bereits bereinigt:
- ✅ `check_*.py` - Gelöscht
- ✅ `fix_*.py` - Gelöscht
- ✅ `validate_person_new.py` - Gelöscht
- ✅ `cleanup_*.py` - Gelöscht

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

**Aktuelle Version**: 2.1 (2025-10-07)

**Neueste Änderungen (v2.1)**:
- ✅ **11 vollständige JSON-Schemata** - Alle Inhaltstypen validiert und produktionsreif
- ✅ **Automatische Schema-Validierung** - `validate_schemas.py` prüft alle Schemata
- ✅ **Workflow ohne Chatbot** - `example_workflow_withoutchatbot.py` für Batch-Verarbeitung
- ✅ **Mehrstufige Validierung** - Schema-Syntax, Struktur, Daten-Typ, Business-Logik
- ✅ **SKOS-Vokabulare** - `occupation.json` und `learning_materials.json` integriert
- ✅ **Prompt-Schema** - Spezial-Schema für KI-Prompts in Bildungskontexten

**Änderungen (v2.0)**:
- ✅ Mehrere Spezial-Schemas nacheinander verarbeiten
- ✅ Interaktive Korrekturen ohne Auto-Weiterleitung
- ✅ Zurück-Navigation zu allen vorherigen Phasen
- ✅ Nummerierte Schema-Auswahl (1,2,3 oder Namen)
- ✅ Flexible Mehrfachauswahl bei Inhaltstypen
- ✅ Phase-History für besseres Tracking

Siehe `docs/CHANGELOG.md` für vollständige Versionshistorie.

---

## 📊 Übersicht: Verfügbare Inhaltstypen

Der Agent unterstützt **11 JSON-Schemata** für verschiedene Bildungsinhalte:

| Schema | Anwendungsfall | Felder | Status |
|--------|----------------|--------|--------|
| 🏛️ **core** | Basis-Metadaten für alle Inhalte | 15 | ✅ Pflicht |
| 👤 **person** | Personen, Experten, Lehrende | 37 | ✅ Valide |
| 📦 **source** | Repositories, Portale, Kanäle | 19 | ✅ Valide |
| 🛠️ **tool_service** | Software, Plattformen, Apps | 28 | ✅ Valide |
| 📅 **event** | Konferenzen, Workshops, Tagungen | 22 | ✅ Valide |
| 🏢 **organization** | Institutionen, Bildungseinrichtungen | 34 | ✅ Valide |
| 🎓 **education_offer** | Kurse, Zertifikate, Studiengänge | 20 | ✅ Valide |
| 📐 **didactic_planning_tools** | Unterrichts- und Planungswerkzeuge | 24 | ✅ Valide |
| 💬 **prompt** | KI-Prompts für Bildungskontexte | JSON Schema | ✅ Valide |
| 💼 **occupation** | Berufe-Taxonomie (SKOS) | 8 Top-Konzepte | ✅ Valide |
| 📚 **learning_materials** | Lernressourcen-Taxonomie (SKOS) | SKOS | ✅ Valide |

---

**Viel Erfolg beim Extrahieren von Metadaten! 🚀**
