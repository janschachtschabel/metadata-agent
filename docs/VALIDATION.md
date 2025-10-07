# 🔍 Validierung & Normalisierung im Metadata-Agent

## Überblick

Die Validierung arbeitet **zweistufig** nach jedem Extraktionsschritt: Zunächst werden die von GPT-5 extrahierten Werte **normalisiert** (bereinigt), anschließend gegen die **Schema-Regeln** validiert. Dieser Prozess stellt sicher, dass alle Metadaten konsistent, sauber und regelkonform gespeichert werden.

## Workflow: Schema → Extraktion → Validierung

### 1. Schema-Definition (core.json, event.json, etc.)

Jedes Feld im Schema enthält Validierungs- und Normalisierungsregeln:

```json
{
  "id": "cclom:title",
  "prompt": {
    "label": "Titel",
    "description": "Aussagekräftiger Titel der Ressource"
  },
  "system": {
    "datatype": "string",
    "required": true,
    "normalization": {
      "trim": true,              // Whitespace entfernen
      "collapseWhitespace": true // Mehrfach-Spaces reduzieren
    }
  }
}
```

Bei **Vocabularies** (kontrollierte Wertelisten):

```json
{
  "id": "cclom:educational_context",
  "vocabulary": {
    "type": "closed",           // Nur definierte Werte erlaubt
    "source": "context_vocab",
    "concepts": [
      {"id": "berufliche_bildung", "label": "Berufliche Bildung"},
      {"id": "hochschule", "label": "Hochschule"}
    ]
  }
}
```

### 2. Extraktion durch GPT-5

Der Agent sendet den User-Text an GPT-5-mini mit allen relevanten Feldern. GPT-5 extrahiert strukturierte Daten:

```python
# Beispiel: User-Input
"Ein Python-Kurs  für  Anfänger   an der Hochschule"

# GPT-5 extrahiert:
{
  "cclom:title": "  Python-Kurs  für  Anfänger  ",
  "cclom:educational_context": "Hochschule"
}
```

### 3. Normalisierung (`validator.normalize_value()`)

Für **jeden** extrahierten Wert wird die Normalisierung aus dem Schema angewendet:

**Regel: `trim: true`**
```python
"  Python-Kurs  " → "Python-Kurs"
```

**Regel: `collapseWhitespace: true`**
```python
"Kurs  für  Anfänger" → "Kurs für Anfänger"
```

**Regel: `lowercase: true`**
```python
"PYTHON" → "python"
```

**Regel: `deduplicate: true` (bei Arrays)**
```python
["Python", "python", "Python"] → ["Python"]
```

### 4. Validierung (`_validate_and_normalize_fields()`)

Nach der Normalisierung werden die Werte gegen Schema-Regeln geprüft:

#### a) **Vocabulary-Validierung** (closed vocabularies)

```python
# Schema definiert: ["Berufliche Bildung", "Hochschule"]
# GPT-5 extrahiert: "Universität"

→ Warnung: "⚠️ Ungültiger Wert: 'Universität' 
            Erlaubt: Berufliche Bildung, Hochschule"
```

#### b) **Datentyp-Validierung**

```python
# Schema: datatype="date"
# GPT-5 extrahiert: "07.10.2025"

→ Warnung: "⚠️ Ungültiges Datumsformat (erwartet: YYYY-MM-DD)"
```

#### c) **Pflichtfeld-Validierung**

```python
# Schema: required=true
# Feld leer oder fehlt

→ Agent fragt nach: "❌ Titel: Bitte angeben"
```

### 5. Ergebnis & Fehlerbehandlung

**Bei erfolgreicher Validierung:**
- Normalisierte, validierte Werte werden im `WorkflowState` gespeichert
- User sieht saubere Daten im UI
- JSON-Export enthält konsistente Metadaten

**Bei Validierungswarnungen:**
- Warnungen werden im **Terminal geloggt** (für Debugging)
- Wert wird trotzdem gespeichert (keine harte Blockierung)
- Agent kann User nach Korrektur fragen

## Integration in den Agent

Die Validierung ist **transparent** in `_extract_fields()` integriert:

```python
def _extract_fields(self, text: str, fields: List[Field], ...):
    # 1. GPT-5 extrahiert Rohwerte
    raw_extracted = gpt5_extract(text, fields)
    
    # 2. Validierung & Normalisierung
    normalized, warnings = self._validate_and_normalize_fields(
        raw_extracted, 
        fields
    )
    
    # 3. Warnungen loggen
    if warnings:
        for w in warnings:
            print(f"🔍 {w}")
    
    # 4. Normalisierte Werte zurückgeben
    return normalized
```

**Wird automatisch aufgerufen bei:**
- Core-Pflichtfelder (Phase 2)
- Core-Optionale Felder (Phase 3)
- Spezial-Schema Pflichtfelder (Phase 5a)
- Spezial-Schema Optionale Felder (Phase 5b)

## Vorteile

✅ **Datenqualität**: Keine Duplikate, konsistentes Whitespace, gültige Formate  
✅ **Schema-Konformität**: Werte entsprechen definierten Vocabularies  
✅ **Automatisch**: Keine manuelle Nachbearbeitung nötig  
✅ **Transparent**: Warnungen im Log für Debugging  
✅ **Flexibel**: Pro Feld konfigurierbar via Schema

## Beispiel: End-to-End

**Input:**
```
"Ein  PYTHON-Kurs   für Anfänger an der Universität"
```

**Extraktion (GPT-5):**
```json
{
  "cclom:title": "  PYTHON-Kurs   für Anfänger  ",
  "cclom:general_keyword": ["Python", "python", "Anfänger"],
  "cclom:educational_context": "Universität"
}
```

**Nach Validierung:**
```json
{
  "cclom:title": "PYTHON-Kurs für Anfänger",
  "cclom:general_keyword": ["Python", "Anfänger"],
  "cclom:educational_context": "Hochschule"
}
```

**Warnungen:**
```
⚠️ educational_context: 'Universität' nicht erlaubt → Korrektur zu 'Hochschule'
```

---

**Fazit:** Die Validierung stellt sicher, dass extrahierte Metadaten **automatisch bereinigt und gegen Schema-Regeln geprüft** werden, bevor sie im Workflow gespeichert werden. Dies garantiert konsistente, hochwertige Metadaten ohne manuelle Nacharbeit.
