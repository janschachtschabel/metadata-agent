# ⚡ Performance-Optimierung

## 🎯 GPT-5 Performance-Einstellungen

Der MetadataAgent unterstützt zwei wichtige Performance-Parameter:

### **1. Reasoning Effort** (Denkaufwand)

Steuert wie viel "Denkzeit" GPT-5 investiert:

```python
agent = MetadataAgent(
    api_key=API_KEY,
    model="gpt-5-mini",
    reasoning_effort="minimal"  # ← Hier anpassen
)
```

| Level | Zeit | Qualität | Anwendungsfall |
|-------|------|----------|----------------|
| **`minimal`** | ~0.5-1s | Gut | ✅ **Empfohlen** für strukturierte Extraktion |
| `low` | ~1-2s | Besser | Komplexere Texte |
| `medium` | ~2-3s | Sehr gut | Mehrdeutige Inhalte |
| `high` | ~3-5s | Maximum | Schwierige Fälle |

**Standard:** `minimal` (optimal für Metadaten-Extraktion)

---

### **2. Verbosity** (Ausführlichkeit)

Steuert die Länge der Antworten:

```python
agent = MetadataAgent(
    api_key=API_KEY,
    model="gpt-5-mini",
    verbosity="low"  # ← Hier anpassen
)
```

| Level | Tokens | Antwort | Anwendungsfall |
|-------|--------|---------|----------------|
| **`low`** | Minimal | Kurz, präzise | ✅ **Empfohlen** für Extraktion |
| `medium` | Normal | Ausgewogen | Erklärungen gewünscht |
| `high` | Viele | Ausführlich | Debugging, Entwicklung |

**Standard:** `low` (minimal Tokens, schnellste Verarbeitung)

---

## 📊 Performance-Vergleich

### **Optimale Einstellungen (Standard):**

```python
agent = MetadataAgent(
    api_key=API_KEY,
    model="gpt-5-mini",
    reasoning_effort="minimal",  # ✅ Schnell
    verbosity="low"              # ✅ Minimal Tokens
)
```

**Erwartete Zeit:** ~5-8 Sekunden (ohne Rate Limits)

---

### **Höhere Qualität (langsamer):**

```python
agent = MetadataAgent(
    api_key=API_KEY,
    model="gpt-5-mini",
    reasoning_effort="low",      # Bessere Qualität
    verbosity="medium"           # Mehr Kontext
)
```

**Erwartete Zeit:** ~10-15 Sekunden

---

### **Maximum Quality (sehr langsam):**

```python
agent = MetadataAgent(
    api_key=API_KEY,
    model="gpt-5-mini",
    reasoning_effort="high",     # Beste Qualität
    verbosity="high"             # Ausführlich
)
```

**Erwartete Zeit:** ~20-30 Sekunden

---

## 🚀 Performance-Tipps

### **1. Optional-Felder überspringen**

Extrahiere nur Pflichtfelder für maximale Geschwindigkeit:

```python
# In example_workflow_withoutchatbot.py:
# Phase 3 (Core Optional) auskommentiert
# Phase 5b (Special Optional) auskommentiert
```

**Einsparung:** ~50% weniger Zeit

---

### **2. Nur 1 Spezialschema**

```python
# Limitiere auf 1 Schema
if state.selected_content_types:
    state.selected_content_types = state.selected_content_types[:1]
    state.special_schemas = state.special_schemas[:1]
```

**Einsparung:** ~30% weniger Zeit bei mehreren erkannten Typen

---

### **3. Rate Limits beachten**

OpenAI Rate Limits können die Performance **massiv** beeinflussen:

```bash
# Teste API-Latenz:
python test_api_latency.py

# Normal:    < 1.5s pro Call
# Langsam:   > 3s pro Call (Rate Limits!)
# Sehr langsam: > 5s pro Call (Retries)
```

**Lösung:**
- Warte 15-60 Minuten
- Upgrade auf höheres Tier bei OpenAI
- Nutze `gpt-4o-mini` (höhere Limits)

---

### **4. Performance messen**

```bash
python compare_performance.py
```

Zeigt exakt, wo Zeit verbraucht wird:

```
phase2_core_required    :   1.85s  ███████████████████ 37.2%
phase3_core_optional    :   1.62s  ████████████████ 32.6%
phase4_schema_detection :   0.89s  ████████ 17.9%
phase5_special          :   0.45s  ████ 9.1%
```

---

## 📝 Beispiele

### **Standard-Workflow** (Empfohlen)

```bash
python example_workflow_withoutchatbot.py
```

- ✅ Nur Pflichtfelder
- ⚡ `reasoning_effort="minimal"`
- ⚡ `verbosity="low"`
- **Zeit:** ~10-12s

---

### **Ultra-Minimal** (Nur Core + Special Required)

```bash
python example_workflow_minimal.py
```

- ✅ Minimale Feldanzahl
- ⚡ Maximale Performance
- **Zeit:** ~5-8s

---

### **Mit allen Feldern** (Vollständig)

```python
# In example_workflow_withoutchatbot.py:
# Phase 3 & 5b aktivieren (uncomment)
state = agent._extract_core_optional_node(state)
state = agent._extract_special_optional_node(state)
```

- ✅ Alle Felder extrahiert
- ⏱️ Längere Laufzeit
- **Zeit:** ~15-20s

---

## 🐛 Troubleshooting

### **Problem: 20+ Sekunden Laufzeit**

**Ursachen:**
1. ❌ OpenAI Rate Limits (Hauptursache!)
2. ❌ Zu viele optionale Felder
3. ❌ Mehrere Spezial-Schemas

**Lösung:**
```bash
# 1. Prüfe Rate Limits
python test_api_latency.py

# 2. Nutze optimierte Version
python example_workflow_minimal.py

# 3. Warte oder wechsle Model
```

---

### **Problem: Schlechte Extraktion**

**Lösung:** Erhöhe reasoning_effort:

```python
agent = MetadataAgent(
    api_key=API_KEY,
    model="gpt-5-mini",
    reasoning_effort="low",  # oder "medium"
    verbosity="low"
)
```

**Trade-off:** +50% Zeit für +20% Qualität

---

## 📊 Zusammenfassung

| Einstellung | Empfehlung | Grund |
|-------------|------------|-------|
| **Model** | `gpt-5-mini` | Beste Balance |
| **Reasoning** | `minimal` | Strukturierte Extraktion |
| **Verbosity** | `low` | Minimal Tokens |
| **Optional-Felder** | Überspringen | 50% schneller |
| **Schemas** | Nur 1 | Fokussiert |

**Standard-Performance:** 5-8 Sekunden ⚡
