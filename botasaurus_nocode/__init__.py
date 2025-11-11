"""
Botasaurus No-Code Visual Builder
==================================

Visual workflow builder for creating scrapers without code.
"""

__version__ = "0.2.0"

from .service import WorkflowService
from .execution_engine import WorkflowExecutionEngine, ExecutionContext
from .router import router as workflow_router
from .templates_router import router as templates_router
from .schemas import (
    WorkflowDefinition,
    WorkflowSettings,
    WorkflowNode,
    NodeConnection,
    NodeType,
    WorkflowStatus,
    CreateWorkflowRequest,
    UpdateWorkflowRequest,
    ExecuteWorkflowRequest,
    WorkflowResponse,
    WorkflowExecutionResponse,
    WorkflowStatistics,
    WorkflowTemplate
)
from .templates import (
    get_all_templates,
    get_template_by_id,
    get_templates_by_category,
    get_template_categories
)

__all__ = [
    # Service
    "WorkflowService",
    "WorkflowExecutionEngine",
    "ExecutionContext",

    # Routers
    "workflow_router",
    "templates_router",

    # Schemas
    "WorkflowDefinition",
    "WorkflowSettings",
    "WorkflowNode",
    "NodeConnection",
    "NodeType",
    "WorkflowStatus",
    "CreateWorkflowRequest",
    "UpdateWorkflowRequest",
    "ExecuteWorkflowRequest",
    "WorkflowResponse",
    "WorkflowExecutionResponse",
    "WorkflowStatistics",
    "WorkflowTemplate",

    # Templates
    "get_all_templates",
    "get_template_by_id",
    "get_templates_by_category",
    "get_template_categories",
]
