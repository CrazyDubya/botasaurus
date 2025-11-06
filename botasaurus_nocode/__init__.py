"""
Botasaurus No-Code Builder
==========================

Visual drag-and-drop scraper builder for non-developers.

Features:
- Visual workflow canvas
- Point-and-click element selection
- Pre-built templates
- No coding required
"""

__version__ = "0.1.0"

from .builder_server import BuilderServer
from .recorder import ActionRecorder
from .workflow_engine import WorkflowEngine

__all__ = ["BuilderServer", "ActionRecorder", "WorkflowEngine"]
