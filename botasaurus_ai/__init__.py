"""
Botasaurus AI Copilot Module
=============================

AI-powered scraper generation from natural language prompts.

Features:
- Natural language to scraper code generation
- Page structure analysis using vision models
- Smart CSS/XPath selector recommendations
- Auto-validation and error fixing
- Interactive refinement chat
"""

__version__ = "0.1.0"

from .copilot import ScraperCopilot
from .code_generator import CodeGenerator
from .page_analyzer import PageAnalyzer
from .selector_finder import SelectorFinder

__all__ = [
    "ScraperCopilot",
    "CodeGenerator",
    "PageAnalyzer",
    "SelectorFinder",
]
