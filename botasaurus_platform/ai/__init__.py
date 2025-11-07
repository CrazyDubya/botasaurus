"""
AI Copilot Module
==================

AI-powered scraper generation, refinement, and analysis.
"""

from .service import AICopilotService
from .router import router as ai_router
from .schemas import (
    GenerateScraperRequest,
    RefineScraperRequest,
    AnalyzePageRequest,
    ValidateCodeRequest,
    GeneratedCode,
    RefinedCode,
    PageAnalysis,
    ValidationResult,
    ConversationResponse,
    UsageStats
)

__all__ = [
    "AICopilotService",
    "ai_router",
    "GenerateScraperRequest",
    "RefineScraperRequest",
    "AnalyzePageRequest",
    "ValidateCodeRequest",
    "GeneratedCode",
    "RefinedCode",
    "PageAnalysis",
    "ValidationResult",
    "ConversationResponse",
    "UsageStats"
]
