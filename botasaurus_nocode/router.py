"""
Workflow API Router
===================

FastAPI routes for visual workflow builder.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.database.models import User
from ..auth.dependencies import get_current_user

from .service import WorkflowService
from .schemas import (
    CreateWorkflowRequest, UpdateWorkflowRequest, ExecuteWorkflowRequest,
    WorkflowResponse, WorkflowExecutionResponse, WorkflowStatistics,
    WorkflowStatus, WorkflowDefinition, CreateScheduleRequest,
    WorkflowSchedule
)


router = APIRouter(prefix="/workflows", tags=["workflows"])


# ==================== Workflow CRUD ====================

@router.post("", response_model=WorkflowResponse, status_code=201)
def create_workflow(
    request: CreateWorkflowRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Create a new workflow.

    Example:
        POST /api/workflows
        {
            "name": "Amazon Product Scraper",
            "description": "Scrape product listings",
            "definition": {
                "nodes": [...],
                "connections": [...]
            },
            "settings": {
                "browser_type": "chromium",
                "headless": true
            },
            "tags": ["e-commerce", "amazon"]
        }
    """
    service = WorkflowService(db, user)

    try:
        return service.create_workflow(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[WorkflowResponse])
def list_workflows(
    status: Optional[WorkflowStatus] = None,
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    List user's workflows.

    Query parameters:
    - status: Filter by status (draft|active|completed|failed)
    - tags: Filter by tags (comma-separated)
    - limit: Number of results (1-100)
    - offset: Pagination offset
    """
    service = WorkflowService(db, user)

    # Parse tags
    tag_list = [t.strip() for t in tags.split(",")] if tags else None

    return service.list_workflows(
        status=status,
        tags=tag_list,
        limit=limit,
        offset=offset
    )


@router.get("/{workflow_id}", response_model=WorkflowResponse)
def get_workflow(
    workflow_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get workflow by ID"""
    service = WorkflowService(db, user)
    workflow = service.get_workflow(workflow_id)

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    return workflow


@router.put("/{workflow_id}", response_model=WorkflowResponse)
def update_workflow(
    workflow_id: UUID,
    request: UpdateWorkflowRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Update workflow.

    You can update any combination of:
    - name
    - description
    - definition (nodes and connections)
    - settings
    - tags
    - status
    """
    service = WorkflowService(db, user)

    try:
        workflow = service.update_workflow(workflow_id, request)

        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")

        return workflow
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{workflow_id}", status_code=204)
def delete_workflow(
    workflow_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Delete workflow"""
    service = WorkflowService(db, user)

    if not service.delete_workflow(workflow_id):
        raise HTTPException(status_code=404, detail="Workflow not found")


@router.post("/{workflow_id}/duplicate", response_model=WorkflowResponse)
def duplicate_workflow(
    workflow_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Duplicate an existing workflow.

    Creates a copy with " (Copy)" appended to the name.
    """
    service = WorkflowService(db, user)
    duplicate = service.duplicate_workflow(workflow_id)

    if not duplicate:
        raise HTTPException(status_code=404, detail="Workflow not found")

    return duplicate


# ==================== Validation ====================

@router.post("/validate", status_code=200)
def validate_workflow(
    definition: WorkflowDefinition,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Validate workflow definition without saving.

    Returns validation errors and warnings.
    """
    service = WorkflowService(db, user)
    return service.validate_workflow(definition)


# ==================== Execution ====================

@router.post("/{workflow_id}/execute", response_model=WorkflowExecutionResponse)
async def execute_workflow(
    workflow_id: UUID,
    request: ExecuteWorkflowRequest = ExecuteWorkflowRequest(),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Execute a workflow.

    Example:
        POST /api/workflows/{id}/execute
        {
            "input_data": {
                "url": "https://example.com",
                "search_term": "laptops"
            },
            "settings_override": {
                "headless": false
            }
        }

    Returns execution result with logs and output data.
    """
    service = WorkflowService(db, user)

    try:
        return await service.execute_workflow(workflow_id, request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(e)}")


@router.get("/{workflow_id}/executions", response_model=List[WorkflowExecutionResponse])
def list_workflow_executions(
    workflow_id: UUID,
    status: Optional[WorkflowStatus] = None,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """List executions for a specific workflow"""
    service = WorkflowService(db, user)
    return service.list_executions(workflow_id=workflow_id, status=status, limit=limit)


@router.get("/executions/{execution_id}", response_model=WorkflowExecutionResponse)
def get_execution(
    execution_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get execution by ID"""
    service = WorkflowService(db, user)
    execution = service.get_execution(execution_id)

    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    return execution


@router.get("/executions", response_model=List[WorkflowExecutionResponse])
def list_all_executions(
    status: Optional[WorkflowStatus] = None,
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """List all user's executions across all workflows"""
    service = WorkflowService(db, user)
    return service.list_executions(status=status, limit=limit)


# ==================== Statistics ====================

@router.get("/{workflow_id}/statistics", response_model=WorkflowStatistics)
def get_workflow_statistics(
    workflow_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Get workflow statistics.

    Returns:
    - Total executions
    - Success/failure counts
    - Average duration
    - Success rate
    - Last execution info
    """
    service = WorkflowService(db, user)
    stats = service.get_workflow_statistics(workflow_id)

    if not stats:
        raise HTTPException(status_code=404, detail="Workflow not found")

    return stats


# ==================== Scheduling ====================

@router.post("/{workflow_id}/schedules", response_model=WorkflowSchedule, status_code=201)
def create_schedule(
    workflow_id: UUID,
    request: CreateScheduleRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Create a schedule for workflow execution.

    Schedule types:
    - once: Run once at next_run_at time
    - hourly: Run every hour
    - daily: Run every day
    - weekly: Run every week
    - monthly: Run every month
    - cron: Custom cron expression

    Example:
        POST /api/workflows/{id}/schedules
        {
            "workflow_id": "uuid",
            "schedule_type": "daily",
            "input_data": {"url": "..."}
        }
    """
    # Ensure workflow_id matches
    request.workflow_id = workflow_id

    service = WorkflowService(db, user)

    try:
        return service.create_schedule(request)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{workflow_id}/schedules", response_model=List[WorkflowSchedule])
def list_workflow_schedules(
    workflow_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """List schedules for a specific workflow"""
    service = WorkflowService(db, user)
    return service.list_schedules(workflow_id=workflow_id)


@router.get("/schedules", response_model=List[WorkflowSchedule])
def list_all_schedules(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """List all user's schedules across all workflows"""
    service = WorkflowService(db, user)
    return service.list_schedules()


@router.delete("/schedules/{schedule_id}", status_code=204)
def delete_schedule(
    schedule_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Delete a schedule"""
    service = WorkflowService(db, user)

    if not service.delete_schedule(schedule_id):
        raise HTTPException(status_code=404, detail="Schedule not found")
