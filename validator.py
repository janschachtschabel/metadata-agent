"""Validation and normalization for extracted metadata."""
import re
from typing import Any, Dict, List, Optional
from schema_loader import Field


class MetadataValidator:
    """Validates and normalizes metadata according to schema rules."""
    
    def __init__(self):
        pass
    
    def normalize_value(self, value: Any, field: Field) -> Any:
        """Apply normalization rules to a field value."""
        if value is None:
            return None
        
        normalization = field.system.get("normalization", {})
        
        # Handle arrays
        if field.multiple and isinstance(value, list):
            normalized = [self._normalize_single(v, normalization) for v in value]
            
            # Deduplicate if specified
            if normalization.get("deduplicate", False):
                normalized = self._deduplicate_list(normalized)
            
            return normalized
        else:
            return self._normalize_single(value, normalization)
    
    def _normalize_single(self, value: Any, rules: Dict) -> Any:
        """Apply normalization rules to a single value."""
        if not isinstance(value, str):
            return value
        
        result = value
        
        # Trim whitespace
        if rules.get("trim", False):
            result = result.strip()
        
        # Collapse whitespace
        if rules.get("collapseWhitespace", False):
            result = re.sub(r'\s+', ' ', result)
        
        # Case transformations
        if rules.get("case") == "upper":
            result = result.upper()
        elif rules.get("case") == "lower":
            result = result.lower()
        elif rules.get("case") == "title":
            result = result.title()
        
        # Language code normalization
        if rules.get("lowercase_lang", False):
            # Normalize language codes like "DE" -> "de"
            if re.match(r'^[A-Z]{2}(-[A-Z]{2})?$', result):
                parts = result.split('-')
                result = parts[0].lower()
                if len(parts) > 1:
                    result += '-' + parts[1].upper()
        
        return result
    
    def _deduplicate_list(self, items: List) -> List:
        """Remove duplicates while preserving order."""
        seen = set()
        result = []
        for item in items:
            # Handle unhashable types
            try:
                if item not in seen:
                    seen.add(item)
                    result.append(item)
            except TypeError:
                # For unhashable types, use string representation
                item_str = str(item)
                if item_str not in seen:
                    seen.add(item_str)
                    result.append(item)
        return result
    
    def validate_value(self, value: Any, field: Field) -> tuple[bool, Optional[str]]:
        """Validate a field value according to schema rules.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if value is None or value == "" or value == []:
            if field.required:
                return False, f"Pflichtfeld '{field.prompt.get('label', field.id)}' ist leer"
            return True, None
        
        # Check validation patterns
        validation = field.system.get("validation", {})
        
        if "pattern" in validation:
            pattern = validation["pattern"]
            
            if field.multiple and isinstance(value, list):
                # Validate each item
                for item in value:
                    if not re.match(pattern, str(item)):
                        return False, f"Wert '{item}' entspricht nicht dem erwarteten Format"
            else:
                if not re.match(pattern, str(value)):
                    return False, f"Wert entspricht nicht dem erwarteten Format: {pattern}"
        
        # Check vocabulary constraints
        vocabulary = field.vocabulary
        if vocabulary and vocabulary.get("type") == "closed":
            allowed_values = [c.get("label") for c in vocabulary.get("concepts", [])]
            
            if field.multiple and isinstance(value, list):
                for item in value:
                    if item not in allowed_values:
                        return False, f"Wert '{item}' ist nicht in der zulässigen Liste"
            else:
                if value not in allowed_values:
                    return False, f"Wert '{value}' ist nicht in der zulässigen Liste"
        
        # Check minimum length
        min_length = field.prompt.get("minLength")
        if min_length and isinstance(value, str):
            if len(value) < min_length:
                return False, f"Wert muss mindestens {min_length} Zeichen lang sein"
        
        return True, None
    
    def map_labels_to_uris(self, value: Any, field: Field) -> Any:
        """Map vocabulary labels to URIs if configured."""
        normalization = field.system.get("normalization", {})
        
        if not normalization.get("map_labels_to_uris", False):
            return value
        
        vocabulary = field.vocabulary
        if not vocabulary:
            return value
        
        # Build mapping
        label_to_uri = {}
        for concept in vocabulary.get("concepts", []):
            label = concept.get("label", "")
            uri = concept.get("uri", "")
            if label and uri:
                label_to_uri[label] = uri
                
                # Also map alternative labels
                alt_labels = concept.get("altLabels", [])
                for alt in alt_labels:
                    label_to_uri[alt] = uri
        
        # Apply mapping
        if field.multiple and isinstance(value, list):
            return [label_to_uri.get(v, v) for v in value]
        else:
            return label_to_uri.get(value, value)
    
    def validate_metadata(self, metadata: Dict[str, Any], fields: List[Field]) -> Dict[str, str]:
        """Validate entire metadata object.
        
        Returns:
            Dict of field_id -> error_message for invalid fields
        """
        errors = {}
        
        for field in fields:
            value = metadata.get(field.id)
            is_valid, error = self.validate_value(value, field)
            
            if not is_valid:
                errors[field.id] = error
        
        return errors
    
    def normalize_metadata(self, metadata: Dict[str, Any], fields: List[Field]) -> Dict[str, Any]:
        """Normalize entire metadata object."""
        normalized = {}
        
        field_map = {f.id: f for f in fields}
        
        for field_id, value in metadata.items():
            field = field_map.get(field_id)
            if field:
                normalized_value = self.normalize_value(value, field)
                # Map labels to URIs if configured
                normalized_value = self.map_labels_to_uris(normalized_value, field)
                normalized[field_id] = normalized_value
            else:
                # Keep unknown fields as-is
                normalized[field_id] = value
        
        return normalized
