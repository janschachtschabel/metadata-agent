"""Schema loader and manager for metadata extraction."""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class Field:
    """Represents a field definition from the schema."""
    id: str
    group: str
    group_label: str
    prompt: Dict[str, Any]
    system: Dict[str, Any]
    
    @property
    def path(self) -> str:
        return self.system["path"]
    
    @property
    def required(self) -> bool:
        return self.system.get("required", False)
    
    @property
    def ask_user(self) -> bool:
        return self.system.get("ask_user", False)
    
    @property
    def ai_fillable(self) -> bool:
        return self.system.get("ai_fillable", False)
    
    @property
    def multiple(self) -> bool:
        return self.system.get("multiple", False)
    
    @property
    def datatype(self) -> str:
        return self.system.get("datatype", "string")
    
    @property
    def vocabulary(self) -> Optional[Dict]:
        return self.system.get("vocabulary")
    
    def get_vocabulary_concepts(self) -> List[Dict]:
        """Get vocabulary concepts if available."""
        vocab = self.vocabulary
        if vocab:
            return vocab.get("concepts", [])
        return []


class SchemaManager:
    """Manages schema loading and field access."""
    
    def __init__(self, schema_dir: str = "schemata"):
        self.schema_dir = Path(schema_dir)
        self.schemas: Dict[str, Dict] = {}
        self.fields_cache: Dict[str, List[Field]] = {}
    
    def load_schema(self, schema_name: str) -> Dict:
        """Load a schema file by name."""
        if schema_name in self.schemas:
            return self.schemas[schema_name]
        
        schema_path = self.schema_dir / schema_name
        if not schema_path.exists():
            schema_path = self.schema_dir / f"{schema_name}.json"
        
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_name}")
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        
        self.schemas[schema_name] = schema
        return schema
    
    def get_fields(self, schema_name: str) -> List[Field]:
        """Get all fields from a schema as Field objects."""
        if schema_name in self.fields_cache:
            return self.fields_cache[schema_name]
        
        schema = self.load_schema(schema_name)
        fields = [
            Field(
                id=f["id"],
                group=f.get("group", ""),
                group_label=f.get("group_label", ""),
                prompt=f.get("prompt", {}),
                system=f.get("system", {})
            )
            for f in schema.get("fields", [])
        ]
        
        self.fields_cache[schema_name] = fields
        return fields
    
    def get_required_fields(self, schema_name: str) -> List[Field]:
        """Get only required fields from a schema."""
        return [f for f in self.get_fields(schema_name) if f.required]
    
    def get_optional_fields(self, schema_name: str) -> List[Field]:
        """Get only optional fields from a schema."""
        return [f for f in self.get_fields(schema_name) if not f.required]
    
    def get_ai_fillable_fields(self, schema_name: str) -> List[Field]:
        """Get fields that can be filled by AI."""
        return [f for f in self.get_fields(schema_name) if f.ai_fillable]
    
    def get_user_ask_fields(self, schema_name: str) -> List[Field]:
        """Get fields that should ask the user."""
        return [f for f in self.get_fields(schema_name) if f.ask_user]
    
    def get_output_template(self, schema_name: str) -> Dict:
        """Get the output template from a schema."""
        schema = self.load_schema(schema_name)
        return schema.get("output_template", {})
    
    def get_content_type_field(self, schema_name: str = "core.json") -> Optional[Field]:
        """Get the content type field (ccm:oeh_flex_lrt) from core schema."""
        fields = self.get_fields(schema_name)
        for field in fields:
            if field.id == "ccm:oeh_flex_lrt":
                return field
        return None
    
    def get_available_special_schemas(self, schema_name: str = "core.json") -> Dict[str, str]:
        """Get available special schemas from the content type field.
        Only returns schemas where the file actually exists.
        
        Returns:
            Dict mapping label to schema_file
        """
        content_type_field = self.get_content_type_field(schema_name)
        if not content_type_field:
            return {}
        
        concepts = content_type_field.get_vocabulary_concepts()
        schema_map = {}
        for concept in concepts:
            label = concept.get("label", "")
            schema_file = concept.get("schema_file", "")
            if label and schema_file:
                # Only add if file exists
                schema_path = os.path.join(self.schema_dir, schema_file)
                if os.path.exists(schema_path):
                    schema_map[label] = schema_file
                else:
                    print(f"⚠️ Schema '{schema_file}' für '{label}' nicht gefunden. Überspringe...")
        
        return schema_map
    
    def merge_templates(self, *schema_names: str) -> Dict:
        """Merge output templates from multiple schemas."""
        merged = {}
        for schema_name in schema_names:
            template = self.get_output_template(schema_name)
            merged.update(template)
        return merged
