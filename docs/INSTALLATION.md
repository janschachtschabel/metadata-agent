# 🛠️ Installations-Anleitung

## Schritt-für-Schritt Installation

### Schritt 1: Python prüfen

```powershell
# Python Version prüfen (mindestens 3.10 erforderlich)
python --version
```

**Falls Python fehlt**: Download von https://www.python.org/downloads/

---

### Schritt 2: Virtual Environment erstellen

```powershell
# Im Projektverzeichnis
cd c:\Users\jan\staging\Windsurf\metadata-agent

# Virtual Environment erstellen
python -m venv venv

# Aktivieren
.\venv\Scripts\activate

# Nach Aktivierung sollte (venv) vor dem Prompt erscheinen
```

---

### Schritt 3: Dependencies installieren

```powershell
# Alle Pakete installieren
pip install -r requirements.txt

# Das dauert ca. 2-3 Minuten
```

**Installierte Pakete**:
- openai (GPT-4o-mini Integration)
- langchain (LLM Framework)
- langgraph (Workflow State Machine)
- gradio (Web UI)
- pydantic (Datenvalidierung)
- python-dotenv (Umgebungsvariablen)

---

### Schritt 4: OpenAI API Key konfigurieren

#### 4.1 API Key erhalten
1. Gehe zu: https://platform.openai.com/api-keys
2. Logge dich ein oder registriere dich
3. Klicke "Create new secret key"
4. Kopiere den Key (beginnt mit `sk-proj-...` oder `sk-...`)

#### 4.2 .env Datei erstellen

```powershell
# Template kopieren
copy .env.example .env

# Mit Notepad öffnen
notepad .env
```

#### 4.3 API Key einfügen

In `.env`:
```
OPENAI_API_KEY=sk-proj-IHR_API_KEY_HIER
```

**💡 Wichtig**: 
- Keine Anführungszeichen
- Keine Leerzeichen um das `=`
- Key muss mit `sk-` beginnen

---

### Schritt 5: Installation testen

```powershell
python test_setup.py
```

**Erwartete Ausgabe**:
```
🧪 Metadata Agent - Setup Test
============================================================
🔍 Testing Python version...
   ✅ Python 3.10.x

🔍 Testing dependencies...
   ✅ OpenAI
   ✅ Langchain
   ✅ Langgraph
   ✅ Gradio
   ✅ Pydantic
   ✅ python-dotenv

🔍 Testing .env configuration...
   ✅ .env file exists
   ✅ OPENAI_API_KEY set: sk-proj-...abc

🔍 Testing schema files...
   ✅ schemata/core.json
   ✅ schemata/event.json

🔍 Testing custom modules...
   ✅ schema_loader.py
   ✅ models.py
   ✅ agent.py
   ✅ validator.py

🔍 Testing schema loading...
   ✅ Core schema loaded (15 fields)
   ✅ Event schema loaded (40+ fields)
   ✅ Field extraction works (3 required fields)

🔍 Testing OpenAI API connection...
   ✅ OpenAI API reachable (model: gpt-4o-mini)

============================================================
📊 Test Summary
============================================================
✅ PASS     Python Version
✅ PASS     Dependencies
✅ PASS     .env Configuration
✅ PASS     Schema Files
✅ PASS     Custom Modules
✅ PASS     Schema Loading
✅ PASS     OpenAI Connection

------------------------------------------------------------
Result: 7/7 tests passed

🎉 All tests passed! You're ready to go!

▶️  Start the app with: python app.py
▶️  Or try the example: python example.py
============================================================
```

---

### Schritt 6: Anwendung starten

#### Option A: Gradio UI (empfohlen)

```powershell
python app.py
```

**Output**:
```
Running on local URL:  http://127.0.0.1:7860

To create a public link, set `share=True` in `launch()`.
```

→ Browser öffnen: http://127.0.0.1:7860

#### Option B: Batch-Script (Windows)

```powershell
.\start.bat
```

Das Script:
- Prüft Virtual Environment
- Installiert Dependencies falls nötig
- Prüft .env Datei
- Startet die App

#### Option C: Beispiel ohne UI

```powershell
python example.py
```

Führt eine vollständige Extraktion im Terminal durch.

---

## 🔧 Troubleshooting

### Problem: "python not found"

**Lösung**:
```powershell
# Python Pfad prüfen
where python

# Falls nicht gefunden, Python neu installieren:
# https://www.python.org/downloads/
# ✅ Häkchen setzen bei "Add Python to PATH"
```

---

### Problem: "pip install" schlägt fehl

**Lösung 1**: pip aktualisieren
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Lösung 2**: Proxy-Probleme
```powershell
# Falls hinter Firewall
pip install -r requirements.txt --proxy http://user:pass@proxy:port
```

**Lösung 3**: Einzeln installieren
```powershell
pip install openai
pip install langchain
pip install langchain-openai
pip install langgraph
pip install gradio
pip install pydantic
pip install python-dotenv
```

---

### Problem: ".env file not found"

**Lösung**:
```powershell
# Prüfe ob Datei existiert
dir .env

# Falls nicht:
copy .env.example .env
notepad .env
# API Key einfügen und speichern
```

---

### Problem: "OPENAI_API_KEY not found"

**Checkliste**:
1. ✅ `.env` Datei existiert (nicht `.env.example`)
2. ✅ Datei enthält: `OPENAI_API_KEY=sk-...`
3. ✅ Keine Leerzeichen um `=`
4. ✅ Keine Anführungszeichen
5. ✅ App neu starten nach .env Änderung

**Test**:
```powershell
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('OPENAI_API_KEY'))"
# Sollte deinen API Key ausgeben
```

---

### Problem: "OpenAI API Error"

**Mögliche Ursachen**:

1. **Ungültiger API Key**
   - Prüfe auf https://platform.openai.com/api-keys
   - Erstelle neuen Key falls nötig

2. **Kein Guthaben**
   - Prüfe: https://platform.openai.com/usage
   - Lade Guthaben auf oder füge Zahlungsmethode hinzu

3. **Rate Limit**
   - Warte 1 Minute
   - Oder verwende anderes Model: `model="gpt-3.5-turbo"`

4. **Internet-Problem**
   - Prüfe Firewall
   - Teste: `ping api.openai.com`

---

### Problem: "Module not found"

**Lösung**:
```powershell
# Stelle sicher dass venv aktiv ist
.\venv\Scripts\activate

# Re-installiere
pip install -r requirements.txt

# Prüfe Installation
pip list
```

---

### Problem: "Schema file not found"

**Lösung**:
```powershell
# Prüfe ob Dateien existieren
dir schemata\core.json
dir schemata\event.json

# Falls fehlend, stelle sicher dass du im richtigen Verzeichnis bist
cd c:\Users\jan\staging\Windsurf\metadata-agent
```

---

### Problem: Gradio startet nicht

**Lösung**:
```powershell
# Port bereits belegt?
netstat -ano | findstr :7860

# Falls belegt, ändere Port in app.py Zeile 186:
# demo.launch(share=False, server_name="127.0.0.1", server_port=7861)

# Oder:
python app.py --server-port 7861
```

---

### Problem: LLM gibt merkwürdige Antworten

**Lösungen**:

1. **Besseres Model verwenden**
   ```python
   # In app.py, Zeile 16:
   agent = MetadataAgent(api_key=API_KEY, model="gpt-4")
   ```

2. **Temperature anpassen**
   ```python
   # In agent.py, Zeile 19:
   temperature=0.3  # Niedriger = deterministischer
   ```

3. **Prompt verbessern**
   - Strukturierte Eingaben
   - Klare Feldnamen
   - Beispiele angeben

---

## 🔄 Updates

### Dependencies aktualisieren

```powershell
pip install --upgrade -r requirements.txt
```

### Projekt aktualisieren (wenn aus Git)

```powershell
git pull
pip install -r requirements.txt
python test_setup.py
```

---

## 🗑️ Deinstallation

```powershell
# Virtual Environment löschen
deactivate
rmdir /s venv

# Projekt-Ordner löschen (optional)
cd ..
rmdir /s metadata-agent
```

---

## 📋 Checkliste nach Installation

- [ ] Python 3.10+ installiert
- [ ] Virtual Environment erstellt und aktiviert
- [ ] Dependencies installiert (`pip list` zeigt alle Pakete)
- [ ] `.env` Datei mit API Key erstellt
- [ ] `test_setup.py` läuft ohne Fehler
- [ ] `python app.py` startet Gradio UI
- [ ] UI ist erreichbar unter http://127.0.0.1:7860
- [ ] Erste Extraktion erfolgreich durchgeführt

---

## 🎓 Nächste Schritte

Nach erfolgreicher Installation:

1. 📖 **QUICKSTART.md lesen** - 5-Minuten Tutorial
2. 🚀 **Erste Extraktion** - Probiere ein Beispiel aus
3. 📚 **README.md lesen** - Vollständige Dokumentation
4. 🔧 **Eigene Schemata** - Erstelle custom schemas
5. 🎨 **UI anpassen** - Modifiziere app.py

---

**Bei Problemen**: Führe zuerst `python test_setup.py` aus um die Ursache zu identifizieren!

**Viel Erfolg! 🎉**
