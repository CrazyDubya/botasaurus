"""
Workflow Templates API Router
==============================

FastAPI routes for workflow templates.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.database.models import User
from ..auth.dependencies import get_current_user

from .schemas import WorkflowTemplate, TemplateCategory, WorkflowResponse
from .templates import (
    get_all_templates,
    get_template_by_id,
    get_templates_by_category,
    get_template_categories
)
from .service import WorkflowService


router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("", response_model=List[WorkflowTemplate])
def list_templates(
    category: Optional[str] = None,
    user: User = Depends(get_current_user)
):
    """
    List all workflow templates.

    Query parameters:
    - category: Filter by category (e-commerce|news|social|data|monitoring)

    Templates are pre-built workflows that can be used as starting points.
    """
    if category:
        return get_templates_by_category(category)

    return get_all_templates()


@router.get("/categories", response_model=List[TemplateCategory])
def list_categories(user: User = Depends(get_current_user)):
    """
    List all template categories.

    Returns categories with template counts.
    """
    return get_template_categories()


@router.get("/{template_id}", response_model=WorkflowTemplate)
def get_template(
    template_id: str,
    user: User = Depends(get_current_user)
):
    """
    Get template by ID.

    Returns the complete template definition that can be used to create a workflow.
    """
    template = get_template_by_id(template_id)

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return template


@router.post("/{template_id}/create", response_model=WorkflowResponse, status_code=201)
def create_workflow_from_template(
    template_id: str,
    name: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Create a new workflow from a template.

    This creates a new workflow in your account based on the template.
    You can then customize it as needed.

    Parameters:
    - name: Optional custom name (defaults to template name)

    Example:
        POST /api/templates/product-listing/create?name=My Amazon Scraper
    """
    template = get_template_by_id(template_id)

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Create workflow from template
    service = WorkflowService(db, user)

    from .schemas import CreateWorkflowRequest

    request = CreateWorkflowRequest(
        name=name or template.name,
        description=template.description,
        definition=template.definition,
        settings=template.settings,
        tags=template.tags
    )

    try:
        return service.create_workflow(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
