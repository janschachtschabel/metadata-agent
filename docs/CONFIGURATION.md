# ⚙️ Konfiguration via .env

Alle wichtigen Einstellungen können über die `.env`-Datei gesteuert werden.

## 🚀 Quick Start

### 1. .env-Datei erstellen

```bash
# Kopiere die Vorlage
cp .env.example .env

# Oder erstelle manuell:
# Windows PowerShell:
Copy-Item .env.example .env

# Linux/Mac:
cp .env.example .env
```

### 2. API Key eintragen

Öffne `.env` und trage deinen OpenAI API Key ein:

```env
OPENAI_API_KEY=sk-proj-...
```

### 3. Fertig!

Der Agent lädt automatisch alle Einstellungen aus der `.env`:

```python
from agent import MetadataAgent

# Lädt automatisch: API Key, Model, Base URL, Reasoning, Verbosity
agent = MetadataAgent()
```

---

## 📋 Verfügbare Einstellungen

### **OPENAI_API_KEY** (Pflicht)

```env
OPENAI_API_KEY=sk-proj-xxxxx
```

**Beschreibung:** Dein OpenAI API Key  
**Bezugsquelle:** https://platform.openai.com/api-keys  
**Erforderlich:** ✅ Ja

---

### **OPENAI_MODEL** (Optional)

```env
OPENAI_MODEL=gpt-5-mini
```

**Beschreibung:** Welches GPT-5 Modell verwendet werden soll  
**Standard:** `gpt-5-mini`  
**Optionen:**
- `gpt-5-mini` - Empfohlen (beste Balance)
- `gpt-5-nano` - Schneller, weniger leistungsfähig

---

### **OPENAI_BASE_URL** (Optional)

```env
# OPENAI_BASE_URL=https://api.openai.com/v1
```

**Beschreibung:** OpenAI API Basis-URL  
**Standard:** `https://api.openai.com/v1` (wenn nicht gesetzt)  
**Anwendungsfälle:**
- Proxy-Server verwenden
- Custom OpenAI Endpoints
- Azure OpenAI Service
- LiteLLM Gateway

**Beispiele:**

```env
# Azure OpenAI
OPENAI_BASE_URL=https://your-resource.openai.azure.com

# LiteLLM Proxy
OPENAI_BASE_URL=http://localhost:4000

# Custom Proxy
OPENAI_BASE_URL=https://proxy.company.com/openai
```

---

## 🔀 Andere Modelle (GPT-4, GPT-3.5, etc.)

Wenn du ein **anderes Modell** als GPT-5 verwendest:

```env
# Beispiel: GPT-4o
OPENAI_API_KEY=sk-proj-xxxxx
OPENAI_MODEL=gpt-4o

# Diese Parameter werden IGNORIERT (nur für GPT-5):
# GPT5_REASONING_EFFORT=minimal
# GPT5_VERBOSITY=low
```

**Automatische API-Auswahl:**
- GPT-5 Modelle (`gpt-5*`): Nutzt Responses API mit reasoning/verbosity
- Andere Modelle: Nutzt Chat Completions API (Standard)

**Unterstützte Modelle:**
- ✅ `gpt-5-mini`, `gpt-5-nano`, `gpt-5`
- ✅ `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`
- ✅ `gpt-3.5-turbo`
- ✅ Kompatible Models via Custom Base URL

---

## 🎯 Empfohlene Konfigurationen

### **Standard (Optimal für Produktion mit GPT-5):**

```env
OPENAI_API_KEY=sk-proj-xxxxx
OPENAI_MODEL=gpt-5-mini
GPT5_REASONING_EFFORT=minimal
GPT5_VERBOSITY=low
```

**Performance:** ⚡ Schnell (~15-20s)  
**Qualität:** ✅ Gut für strukturierte Extraktion  
**Kosten:** 💰 Niedrig

---

### **Hohe Qualität (für schwierige Texte):**

```env
OPENAI_API_KEY=sk-proj-xxxxx
OPENAI_MODEL=gpt-5-mini
GPT5_REASONING_EFFORT=low
GPT5_VERBOSITY=medium
```

**Performance:** 🐌 Langsamer (~30-40s)  
**Qualität:** ✅✅ Besser bei komplexen Texten  
**Kosten:** 💰💰 Mittel

---

### **Development/Debugging (mit GPT-5):**

```env
OPENAI_API_KEY=sk-proj-xxxxx
OPENAI_MODEL=gpt-5-mini
GPT5_REASONING_EFFORT=medium
GPT5_VERBOSITY=high
```

**Performance:** 🐌🐌 Langsam (~50-80s)  
**Qualität:** ✅✅✅ Maximum + Detaillierte Antworten  
**Kosten:** 💰💰💰 Hoch

---

### **Alternative: GPT-4o (Wenn GPT-5 nicht verfügbar):**

```env
OPENAI_API_KEY=sk-proj-xxxxx
OPENAI_MODEL=gpt-4o
# GPT5_REASONING_EFFORT und GPT5_VERBOSITY werden ignoriert
```

**Performance:** ⚡ Schnell (~10-15s)  
**Qualität:** ✅✅ Sehr gut für strukturierte Extraktion  
**Kosten:** 💰💰 Mittel  
**Note:** Nutzt automatisch Chat Completions API mit temperature=0.1

---

## 🔧 Erweiterte Nutzung

### **Parameter in Code überschreiben:**

Du kannst die .env-Werte auch im Code überschreiben:

```python
from agent import MetadataAgent

# Nutzt .env für alles außer reasoning_effort
agent = MetadataAgent(reasoning_effort="high")

# Überschreibt mehrere Werte
agent = MetadataAgent(
    model="gpt-5-nano",
    reasoning_effort="low",
    verbosity="medium"
)

# Komplett manuell (ignoriert .env)
agent = MetadataAgent(
    api_key="sk-proj-xxxxx",
    model="gpt-5-mini",
    base_url="https://custom.api.com",
    reasoning_effort="minimal",
    verbosity="low"
)
```

---

### **Verschiedene Umgebungen:**

```bash
# Development
.env.development

# Production
.env.production

# Testing
.env.test
```

**Laden:**

```python
from dotenv import load_dotenv

# Lade spezifische .env
load_dotenv('.env.production')

agent = MetadataAgent()
```

---

## 🔍 Troubleshooting

### **Fehler: "OPENAI_API_KEY not provided"**

**Ursache:** `.env` fehlt oder API Key nicht gesetzt

**Lösung:**

```bash
# 1. Prüfe ob .env existiert
ls -la .env

# 2. Erstelle .env aus Vorlage
cp .env.example .env

# 3. Trage API Key ein
# Öffne .env und setze: OPENAI_API_KEY=sk-proj-xxxxx
```

---

### **Fehler: "Invalid GPT-5 model"**

**Ursache:** Ungültiges Model in `.env`

**Lösung:**

```env
# Nur diese Werte erlaubt:
OPENAI_MODEL=gpt-5-mini  # ✅
OPENAI_MODEL=gpt-5-nano  # ✅
OPENAI_MODEL=gpt-4       # ❌ Nicht unterstützt
```

---

### **Langsame Performance (>30s)**

**Ursachen:**
1. `GPT5_REASONING_EFFORT` zu hoch gesetzt
2. `GPT5_VERBOSITY` zu hoch gesetzt
3. OpenAI Rate Limits

**Lösung:**

```env
# Setze auf optimale Werte:
GPT5_REASONING_EFFORT=minimal
GPT5_VERBOSITY=low
```

**Test:**

```bash
# Messe aktuelle Performance:
python test_api_latency.py

# Erwartete Zeit pro Call:
# ✅ <1.5s: Optimal
# ⚠️ 1.5-3s: Akzeptabel
# ❌ >3s: Rate Limits oder zu hohe Einstellungen
```

---

### **Base URL funktioniert nicht**

**Beispiel:** Azure OpenAI

```env
# ❌ Falsch (v1 fehlt):
OPENAI_BASE_URL=https://your-resource.openai.azure.com

# ✅ Richtig:
OPENAI_BASE_URL=https://your-resource.openai.azure.com/openai/deployments/YOUR-DEPLOYMENT-NAME
```

---

## 📊 Performance-Matrix

| reasoning_effort | verbosity | Zeit/Workflow | Qualität | Kosten |
|------------------|-----------|---------------|----------|--------|
| minimal | low | ~15-20s | ⭐⭐⭐ | 💰 |
| minimal | medium | ~20-25s | ⭐⭐⭐ | 💰💰 |
| low | low | ~25-30s | ⭐⭐⭐⭐ | 💰💰 |
| low | medium | ~30-40s | ⭐⭐⭐⭐ | 💰💰💰 |
| medium | low | ~40-50s | ⭐⭐⭐⭐⭐ | 💰💰💰 |
| medium | medium | ~50-60s | ⭐⭐⭐⭐⭐ | 💰💰💰💰 |
| high | high | ~80-120s | ⭐⭐⭐⭐⭐ | 💰💰💰💰💰 |

**Empfehlung:** `minimal` + `low` = Beste Balance! ⚡

---

## ✅ Zusammenfassung

### **Minimale Konfiguration (Nur API Key):**

```env
OPENAI_API_KEY=sk-proj-xxxxx
```

Alle anderen Werte werden automatisch auf optimale Defaults gesetzt!

### **Code bleibt einfach:**

```python
# Alles aus .env
agent = MetadataAgent()
```

### **Flexibel bei Bedarf:**

```python
# Überschreibe einzelne Werte
agent = MetadataAgent(reasoning_effort="high")
```

**Fertig! 🎉**
