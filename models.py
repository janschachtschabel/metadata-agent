"""Pydantic models for metadata extraction workflow."""
from typing import Dict, List, Optional, Any, Literal
from pydantic import BaseModel, Field
from enum import Enum


class WorkflowPhase(str, Enum):
    """Current phase of the metadata extraction workflow."""
    INIT = "init"
    SUGGEST_SPECIAL_SCHEMAS = "suggest_special_schemas"
    EXTRACT_CORE_REQUIRED = "extract_core_required"
    EXTRACT_CORE_OPTIONAL = "extract_core_optional"
    EXTRACT_SPECIAL_REQUIRED = "extract_special_required"
    EXTRACT_SPECIAL_OPTIONAL = "extract_special_optional"
    REVIEW = "review"
    COMPLETE = "complete"


class Message(BaseModel):
    """A chat message."""
    role: Literal["user", "assistant", "system"]
    content: str


class FieldStatus(BaseModel):
    """Status of a field in the extraction process."""
    field_id: str
    field_label: str
    value: Any = None
    is_filled: bool = False
    is_confirmed: bool = False
    is_required: bool = False
    ai_suggested: bool = False
    needs_user_input: bool = False


class WorkflowState(BaseModel):
    """State of the metadata extraction workflow."""
    # Current phase
    phase: WorkflowPhase = WorkflowPhase.INIT
    
    # Loaded schemas
    core_schema: str = "core.json"
    special_schemas: List[str] = Field(default_factory=list)
    selected_content_types: List[str] = Field(default_factory=list)
    
    # Chat history
    messages: List[Message] = Field(default_factory=list)
    
    # Extracted metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Field tracking
    field_status: Dict[str, FieldStatus] = Field(default_factory=dict)
    
    # Current field being processed
    current_field_id: Optional[str] = None
    
    # Pending questions
    pending_questions: List[str] = Field(default_factory=list)
    
    # User input buffer
    user_input: str = ""
    
    # Workflow progress
    core_required_complete: bool = False
    core_optional_complete: bool = False
    special_schema_confirmed: bool = False
    special_required_complete: bool = False
    special_optional_complete: bool = False
    
    # Current special schema being processed
    current_special_schema_index: int = 0
    
    # Navigation history for back button
    phase_history: List[WorkflowPhase] = Field(default_factory=list)
    
    def add_message(self, role: str, content: str):
        """Add a message to the chat history."""
        self.messages.append(Message(role=role, content=content))
    
    def save_phase_to_history(self):
        """Save current phase to history for back navigation."""
        if not self.phase_history or self.phase_history[-1] != self.phase:
            self.phase_history.append(self.phase)
    
    def go_back_phase(self) -> bool:
        """Go back to previous phase. Returns True if successful."""
        if len(self.phase_history) > 1:
            self.phase_history.pop()  # Remove current
            self.phase = self.phase_history[-1]  # Go to previous
            return True
        return False
    
    def update_field(self, field_id: str, value: Any, confirmed: bool = False, ai_suggested: bool = False):
        """Update a field's value and status."""
        if field_id not in self.field_status:
            # Initialize field status if not exists
            self.field_status[field_id] = FieldStatus(
                field_id=field_id,
                field_label=field_id,
                is_required=False
            )
        
        self.field_status[field_id].value = value
        self.field_status[field_id].is_filled = value is not None and value != "" and value != []
        self.field_status[field_id].is_confirmed = confirmed
        self.field_status[field_id].ai_suggested = ai_suggested
        
        # Update metadata
        self.metadata[field_id] = value
    
    def get_unfilled_required_fields(self) -> List[str]:
        """Get list of required fields that are not yet filled."""
        return [
            field_id
            for field_id, status in self.field_status.items()
            if status.is_required and not status.is_filled
        ]
    
    def get_filled_fields(self) -> Dict[str, Any]:
        """Get all filled fields as a dictionary."""
        return {
            field_id: status.value
            for field_id, status in self.field_status.items()
            if status.is_filled
        }
    
    def check_core_required_complete(self) -> bool:
        """Check if all core required fields are filled."""
        required_fields = [
            field_id
            for field_id, status in self.field_status.items()
            if status.is_required and field_id in ["cclom:title", "cclom:general_description", "cclom:general_keyword"]
        ]
        return all(
            self.field_status.get(field_id, FieldStatus(field_id=field_id, field_label=field_id)).is_filled
            for field_id in required_fields
        )


class ExtractionRequest(BaseModel):
    """Request for metadata extraction from user input."""
    user_text: str
    fields_to_extract: List[str]
    current_metadata: Dict[str, Any] = Field(default_factory=dict)


class ExtractionResponse(BaseModel):
    """Response from LLM metadata extraction."""
    extracted_data: Dict[str, Any]
    confidence: float = 1.0
    questions: List[str] = Field(default_factory=list)
