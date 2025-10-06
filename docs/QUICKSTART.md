# 🚀 Quickstart Guide

## Schnellinstallation (5 Minuten)

### 1. Python-Umgebung vorbereiten

```bash
# Virtual Environment erstellen
python -m venv venv

# Aktivieren
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 2. Dependencies installieren

```bash
pip install -r requirements.txt
```

### 3. OpenAI API Key konfigurieren

```bash
# .env Datei erstellen
copy .env.example .env

# Editiere .env und füge deinen API Key ein:
# OPENAI_API_KEY=sk-proj-...
```

> **API Key erhalten**: https://platform.openai.com/api-keys

### 4. Starten!

**Option A: Gradio UI (empfohlen)**
```bash
python app.py
```
→ Öffne Browser: http://127.0.0.1:7860

**Option B: Beispiel-Script (ohne UI)**
```bash
python example.py
```

---

## 📖 Erste Schritte im UI

### Schritt 1: Ressource beschreiben
```
Ich möchte eine Online-Konferenz zum Thema KI in der Hochschullehre 
dokumentieren. Der Titel ist "Zukunft der Hochschullehre 2026" und 
findet am 15. September 2026 statt.
```

### Schritt 2: Inhaltsart bestätigen
```
Agent: Ich erkenne: Veranstaltung. Ist das korrekt?
Du: ja
```

### Schritt 3: Felder ergänzen
```
Agent: Bitte ergänzen Sie: Keywords?
Du: KI, Hochschuldidaktik, Digitale Lehre
```

### Schritt 4: Optional weiter
```
Du: weiter
```

### Schritt 5: JSON herunterladen
- Klicke auf "💾 JSON herunterladen"

---

## 🎯 Wichtige Befehle im Chat

| Befehl | Aktion |
|--------|--------|
| `ja` / `nein` | Inhaltsart bestätigen |
| `weiter` / `next` | Nächster Schritt |
| `skip` | Optionale Felder überspringen |

---

## 🔧 Troubleshooting

### Problem: "OPENAI_API_KEY not found"
**Lösung**: 
1. Erstelle `.env` Datei (nicht `.env.example`)
2. Füge ein: `OPENAI_API_KEY=sk-...`
3. Starte App neu

### Problem: "Schema file not found"
**Lösung**: 
- Stelle sicher dass `schemata/core.json` existiert
- Für Veranstaltungen: `schemata/event.json` muss vorhanden sein

### Problem: App startet nicht
**Lösung**:
```bash
# Dependencies neu installieren
pip install --upgrade -r requirements.txt

# Python Version prüfen (min 3.10)
python --version
```

### Problem: LLM antwortet ungenau
**Lösung**: In `app.py`, ändere Modell:
```python
agent = MetadataAgent(api_key=API_KEY, model="gpt-4")  # Besseres Modell
```

---

## 📚 Beispiel-Prompts

### Veranstaltung
```
Workshop "Prompt Engineering für Lehrende" am 10.06.2026 in München.
Dauer: 3 Stunden. Zielgruppe: Hochschullehrende. 
Keywords: KI, Prompts, Didaktik
```

### Person
```
Prof. Dr. Maria Schmidt ist Expertin für digitale Bildung an der 
TU München. Forschungsschwerpunkte: KI in der Lehre, Learning Analytics.
Email: m.schmidt@tum.de
```

### Lernmaterial
```
Interaktives Tutorial "Python Grundlagen" für Anfänger. 
45 Minuten Videokurs mit Übungen. Lizenz: CC BY-SA 4.0.
Themen: Variablen, Schleifen, Funktionen.
```

---

## 🎨 UI-Bereiche

### 1. Chat (links)
- Konversation mit dem Agent
- Eingabefeld unten
- Buttons: Senden, Neu starten, Chat löschen

### 2. Zwischenergebnisse (rechts oben)
- ✅ **Bestätigt**: Vom User validierte Daten
- 🤖 **KI-Vorschlag**: Automatisch extrahierte Daten
- **Status**: Aktuelle Workflow-Phase

### 3. JSON Vorschau (unten)
- Echtzeit-Vorschau der Metadaten
- Download-Button für Export
- Syntax-Highlighting

---

## 🔄 Workflow-Phasen

```
[1] INIT
    ↓ Beschreibung eingeben
[2] SUGGEST_SPECIAL_SCHEMAS  
    ↓ Inhaltsart bestätigen
[3] EXTRACT_CORE_REQUIRED
    ↓ Pflichtfelder (Titel, Beschreibung, Keywords)
[4] EXTRACT_CORE_OPTIONAL
    ↓ "weiter" oder Felder ergänzen
[5] EXTRACT_SPECIAL_SCHEMA
    ↓ Typspezifische Felder (z.B. Event-Datum)
[6] REVIEW
    ↓ JSON-Export
[7] COMPLETE ✅
```

---

## 📁 Wichtige Dateien

| Datei | Zweck |
|-------|-------|
| `app.py` | Gradio UI - **Hier starten!** |
| `agent.py` | Workflow-Logik (Langgraph) |
| `schema_loader.py` | Schema-Management |
| `models.py` | Datenmodelle (Pydantic) |
| `validator.py` | Validierung & Normalisierung |
| `example.py` | Beispiel ohne UI |
| `schemata/core.json` | Basis-Metadaten |
| `schemata/event.json` | Event-spezifisch |

---

## 💡 Tipps & Tricks

### Tipp 1: Strukturierte Eingabe
✅ **Gut**: 
```
Titel: Workshop XYZ
Datum: 01.03.2026
Thema: KI
```

❌ **Weniger gut**: 
```
Irgendwas mit KI nächstes Jahr
```

### Tipp 2: Mehrere Werte
Für Listen (Keywords, Themen) kannst du verwenden:
- Komma-getrennt: `KI, Didaktik, Online`
- Nummeriert: `1. KI, 2. Didaktik, 3. Online`
- Aufzählung: `- KI, - Didaktik, - Online`

### Tipp 3: Schrittweise vorgehen
- Erst **Pflichtfelder** ausfüllen
- Dann **optionale Felder**
- Mit "weiter" bestätigen

### Tipp 4: JSON editieren
Nach dem Export kannst du das JSON manuell nachbearbeiten:
1. JSON herunterladen
2. In Editor öffnen
3. Anpassen
4. Validieren auf jsonlint.com

---

## 🎓 Nächste Schritte

1. ✅ **Erste Extraktion durchführen** (siehe oben)
2. 📖 **README.md lesen** für Details
3. 🔧 **Eigene Schemata erstellen** in `schemata/`
4. 🚀 **Produktiv einsetzen** mit Session-Management

---

## 📞 Support

Bei Problemen:
1. README.md → Troubleshooting-Sektion
2. Check `python example.py` für Debugging
3. Logs prüfen in der Konsole
4. OpenAI Status: https://status.openai.com

---

**Viel Erfolg! 🎉**
