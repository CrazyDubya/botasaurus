"""
AI API Schemas
===============

Pydantic models for AI Copilot API requests and responses.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


# ==================== Request Models ====================

class GenerateScraperRequest(BaseModel):
    """Request to generate a new scraper from natural language"""
    prompt: str = Field(..., description="Natural language description of scraping task")
    url: Optional[str] = Field(None, description="Target URL to analyze")
    use_vision: bool = Field(True, description="Use vision analysis for page structure")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    conversation_id: Optional[UUID] = Field(None, description="Conversation ID for context")


class RefineScraperRequest(BaseModel):
    """Request to refine existing scraper code"""
    current_code: str = Field(..., description="Current scraper code")
    refinement_prompt: str = Field(..., description="What to change/improve")
    conversation_id: UUID = Field(..., description="Conversation ID for history")


class AnalyzePageRequest(BaseModel):
    """Request to analyze page structure"""
    url: Optional[str] = Field(None, description="URL to analyze")
    html: Optional[str] = Field(None, description="HTML content to analyze")
    screenshot: Optional[bytes] = Field(None, description="Screenshot bytes")
    use_vision: bool = Field(True, description="Use vision model analysis")


class ValidateCodeRequest(BaseModel):
    """Request to validate scraper code"""
    code: str = Field(..., description="Python code to validate")
    url: Optional[str] = Field(None, description="Target URL")
    test_execution: bool = Field(False, description="Actually run the code (dangerous!)")


class AutoFixRequest(BaseModel):
    """Request to automatically fix validation errors"""
    code: str = Field(..., description="Code with errors")
    validation_result: Dict[str, Any] = Field(..., description="Validation result")
    conversation_id: Optional[UUID] = Field(None, description="Conversation ID")


# ==================== Response Models ====================

class GeneratedCode(BaseModel):
    """Generated scraper code result"""
    code: str = Field(..., description="Generated Python code")
    explanation: str = Field(..., description="Plain English explanation")
    selectors: List[str] = Field(default_factory=list, description="CSS/XPath selectors used")
    warnings: List[str] = Field(default_factory=list, description="Potential issues")
    conversation_id: UUID = Field(..., description="Conversation ID")
    tokens_used: int = Field(..., description="LLM tokens consumed")


class RefinedCode(BaseModel):
    """Refined scraper code result"""
    code: str = Field(..., description="Updated code")
    explanation: str = Field(..., description="What changed")
    changes: List[str] = Field(default_factory=list, description="Specific changes made")
    conversation_id: UUID = Field(..., description="Conversation ID")
    tokens_used: int = Field(..., description="LLM tokens consumed")


class PageAnalysis(BaseModel):
    """Page structure analysis result"""
    page_type: str = Field(..., description="Type of page (e-commerce, blog, etc.)")
    complexity: str = Field(..., description="Complexity level (low/medium/high)")
    main_content: List[str] = Field(default_factory=list, description="Main content areas")
    data_patterns: List[str] = Field(default_factory=list, description="Data patterns found")
    recommended_selectors: List[Dict[str, str]] = Field(default_factory=list, description="Suggested selectors")
    recommended_approach: Optional[str] = Field(None, description="@browser or @request")
    key_elements: List[str] = Field(default_factory=list, description="Key page elements")


class ValidationResult(BaseModel):
    """Code validation result"""
    valid: bool = Field(..., description="Whether code is valid")
    errors: List[str] = Field(default_factory=list, description="Error messages")
    warnings: List[str] = Field(default_factory=list, description="Warning messages")
    fixable: bool = Field(..., description="Whether errors are auto-fixable")
    error_count: int = Field(..., description="Number of errors")
    warning_count: int = Field(..., description="Number of warnings")


class AutoFixResult(BaseModel):
    """Auto-fix result"""
    fixed_code: str = Field(..., description="Fixed code")
    fixes_applied: List[str] = Field(default_factory=list, description="Fixes that were applied")
    validation_result: ValidationResult = Field(..., description="Validation of fixed code")
    success: bool = Field(..., description="Whether fix was successful")


# ==================== Conversation Models ====================

class ConversationMessage(BaseModel):
    """Single message in AI conversation"""
    id: UUID
    conversation_id: UUID
    role: str = Field(..., description="user or assistant")
    content: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """AI conversation with history"""
    id: UUID
    user_id: UUID
    title: str
    messages: List[ConversationMessage] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CreateConversationRequest(BaseModel):
    """Request to create new conversation"""
    title: str = Field(..., description="Conversation title")
    initial_prompt: Optional[str] = Field(None, description="First prompt")


# ==================== Usage Models ====================

class UsageStats(BaseModel):
    """AI usage statistics"""
    total_tokens: int = Field(..., description="Total tokens used")
    total_cost: float = Field(..., description="Total cost in USD")
    requests_count: int = Field(..., description="Number of API requests")
    successful_generations: int = Field(..., description="Successful generations")
    failed_generations: int = Field(..., description="Failed generations")


class UsageRecord(BaseModel):
    """Single usage record"""
    id: UUID
    user_id: UUID
    feature: str = Field(..., description="Feature used (generate, refine, analyze, etc.)")
    tokens_used: int
    cost: float
    model: str
    success: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Streaming Models ====================

class StreamChunk(BaseModel):
    """Chunk of streamed response"""
    type: str = Field(..., description="chunk type: code|explanation|complete|error")
    content: str = Field(..., description="Chunk content")
    metadata: Optional[Dict[str, Any]] = None


class StreamComplete(BaseModel):
    """Final message when streaming completes"""
    type: str = Field(default="complete")
    conversation_id: UUID
    tokens_used: int
    warnings: List[str] = Field(default_factory=list)
    selectors: List[str] = Field(default_factory=list)
