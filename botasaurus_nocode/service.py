"""
Workflow Service
================

Business logic for workflow management and execution.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..core.database.models import (
    Workflow, WorkflowRun, WorkflowSchedule as DBWorkflowSchedule, User
)
from .schemas import (
    WorkflowDefinition, WorkflowSettings, WorkflowResponse,
    WorkflowExecutionResponse, WorkflowStatistics, WorkflowStatus,
    CreateWorkflowRequest, UpdateWorkflowRequest, ExecuteWorkflowRequest,
    ExecutionLogEntry, WorkflowSchedule, CreateScheduleRequest, ScheduleType
)
from .execution_engine import WorkflowExecutionEngine


class WorkflowService:
    """Service for managing workflows"""

    def __init__(self, db: Session, user: User, ai_service=None):
        self.db = db
        self.user = user
        self.execution_engine = WorkflowExecutionEngine(ai_service)

    # ==================== CRUD Operations ====================

    def create_workflow(self, request: CreateWorkflowRequest) -> WorkflowResponse:
        """Create new workflow"""

        workflow = Workflow(
            id=uuid4(),
            user_id=self.user.id,
            name=request.name,
            description=request.description,
            definition=request.definition.model_dump(),
            settings=request.settings.model_dump(),
            status=WorkflowStatus.DRAFT,
            tags=request.tags,
            execution_count=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self.db.add(workflow)
        self.db.commit()
        self.db.refresh(workflow)

        return self._to_response(workflow)

    def get_workflow(self, workflow_id: UUID) -> Optional[WorkflowResponse]:
        """Get workflow by ID"""

        workflow = self.db.query(Workflow).filter(
            Workflow.id == workflow_id,
            Workflow.user_id == self.user.id
        ).first()

        if not workflow:
            return None

        return self._to_response(workflow)

    def list_workflows(
        self,
        status: Optional[WorkflowStatus] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[WorkflowResponse]:
        """List user's workflows"""

        query = self.db.query(Workflow).filter(
            Workflow.user_id == self.user.id
        )

        # Filter by status
        if status:
            query = query.filter(Workflow.status == status)

        # Filter by tags
        if tags:
            for tag in tags:
                query = query.filter(Workflow.tags.contains([tag]))

        # Order and paginate
        workflows = query.order_by(
            desc(Workflow.updated_at)
        ).limit(limit).offset(offset).all()

        return [self._to_response(w) for w in workflows]

    def update_workflow(
        self,
        workflow_id: UUID,
        request: UpdateWorkflowRequest
    ) -> Optional[WorkflowResponse]:
        """Update workflow"""

        workflow = self.db.query(Workflow).filter(
            Workflow.id == workflow_id,
            Workflow.user_id == self.user.id
        ).first()

        if not workflow:
            return None

        # Update fields
        if request.name is not None:
            workflow.name = request.name

        if request.description is not None:
            workflow.description = request.description

        if request.definition is not None:
            workflow.definition = request.definition.model_dump()

        if request.settings is not None:
            workflow.settings = request.settings.model_dump()

        if request.tags is not None:
            workflow.tags = request.tags

        if request.status is not None:
            workflow.status = request.status

        workflow.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(workflow)

        return self._to_response(workflow)

    def delete_workflow(self, workflow_id: UUID) -> bool:
        """Delete workflow"""

        workflow = self.db.query(Workflow).filter(
            Workflow.id == workflow_id,
            Workflow.user_id == self.user.id
        ).first()

        if not workflow:
            return False

        self.db.delete(workflow)
        self.db.commit()
        return True

    def duplicate_workflow(self, workflow_id: UUID) -> Optional[WorkflowResponse]:
        """Duplicate existing workflow"""

        original = self.db.query(Workflow).filter(
            Workflow.id == workflow_id,
            Workflow.user_id == self.user.id
        ).first()

        if not original:
            return None

        # Create duplicate
        duplicate = Workflow(
            id=uuid4(),
            user_id=self.user.id,
            name=f"{original.name} (Copy)",
            description=original.description,
            definition=original.definition,
            settings=original.settings,
            status=WorkflowStatus.DRAFT,
            tags=original.tags,
            execution_count=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self.db.add(duplicate)
        self.db.commit()
        self.db.refresh(duplicate)

        return self._to_response(duplicate)

    # ==================== Execution ====================

    async def execute_workflow(
        self,
        workflow_id: UUID,
        request: ExecuteWorkflowRequest
    ) -> WorkflowExecutionResponse:
        """Execute workflow"""

        # Get workflow
        workflow = self.db.query(Workflow).filter(
            Workflow.id == workflow_id,
            Workflow.user_id == self.user.id
        ).first()

        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        # Parse definition and settings
        definition = WorkflowDefinition(**workflow.definition)
        settings = WorkflowSettings(**workflow.settings)

        # Override settings if provided
        if request.settings_override:
            settings = request.settings_override

        # Create execution record
        execution = WorkflowRun(
            id=uuid4(),
            workflow_id=workflow_id,
            user_id=self.user.id,
            status=WorkflowStatus.RUNNING,
            started_at=datetime.utcnow(),
            input_data=request.input_data,
            created_at=datetime.utcnow()
        )

        self.db.add(execution)
        self.db.commit()

        # Execute workflow
        try:
            context = await self.execution_engine.execute(
                workflow=definition,
                input_data=request.input_data,
                settings=settings
            )

            # Update execution record
            execution.status = context.status
            execution.completed_at = datetime.utcnow()
            execution.duration_seconds = (
                execution.completed_at - execution.started_at
            ).total_seconds()
            execution.output_data = context.get_all_data()
            execution.logs = [log.model_dump() for log in context.logs]
            execution.error = context.error

            # Update workflow stats
            workflow.execution_count += 1
            workflow.last_executed_at = datetime.utcnow()

        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.completed_at = datetime.utcnow()
            execution.error = str(e)
            execution.logs = []

        self.db.commit()
        self.db.refresh(execution)

        return self._execution_to_response(execution)

    def get_execution(self, execution_id: UUID) -> Optional[WorkflowExecutionResponse]:
        """Get execution by ID"""

        execution = self.db.query(WorkflowRun).filter(
            WorkflowRun.id == execution_id,
            WorkflowRun.user_id == self.user.id
        ).first()

        if not execution:
            return None

        return self._execution_to_response(execution)

    def list_executions(
        self,
        workflow_id: Optional[UUID] = None,
        status: Optional[WorkflowStatus] = None,
        limit: int = 50
    ) -> List[WorkflowExecutionResponse]:
        """List workflow executions"""

        query = self.db.query(WorkflowRun).filter(
            WorkflowRun.user_id == self.user.id
        )

        if workflow_id:
            query = query.filter(WorkflowRun.workflow_id == workflow_id)

        if status:
            query = query.filter(WorkflowRun.status == status)

        executions = query.order_by(
            desc(WorkflowRun.started_at)
        ).limit(limit).all()

        return [self._execution_to_response(e) for e in executions]

    # ==================== Statistics ====================

    def get_workflow_statistics(self, workflow_id: UUID) -> Optional[WorkflowStatistics]:
        """Get workflow statistics"""

        workflow = self.db.query(Workflow).filter(
            Workflow.id == workflow_id,
            Workflow.user_id == self.user.id
        ).first()

        if not workflow:
            return None

        # Get executions
        executions = self.db.query(WorkflowRun).filter(
            WorkflowRun.workflow_id == workflow_id
        ).all()

        total = len(executions)
        successful = sum(1 for e in executions if e.status == WorkflowStatus.COMPLETED)
        failed = sum(1 for e in executions if e.status == WorkflowStatus.FAILED)

        # Calculate average duration
        completed_execs = [e for e in executions if e.duration_seconds is not None]
        avg_duration = (
            sum(e.duration_seconds for e in completed_execs) / len(completed_execs)
            if completed_execs else 0.0
        )

        # Get last execution
        last_exec = max(executions, key=lambda e: e.started_at) if executions else None

        success_rate = (successful / total * 100) if total > 0 else 0.0

        return WorkflowStatistics(
            total_executions=total,
            successful_executions=successful,
            failed_executions=failed,
            average_duration_seconds=avg_duration,
            last_execution_status=last_exec.status if last_exec else None,
            last_execution_at=last_exec.started_at if last_exec else None,
            success_rate=success_rate
        )

    # ==================== Scheduling ====================

    def create_schedule(
        self,
        request: CreateScheduleRequest
    ) -> WorkflowSchedule:
        """Create workflow schedule"""

        # Verify workflow exists
        workflow = self.db.query(Workflow).filter(
            Workflow.id == request.workflow_id,
            Workflow.user_id == self.user.id
        ).first()

        if not workflow:
            raise ValueError(f"Workflow {request.workflow_id} not found")

        # Calculate next run time
        next_run = self._calculate_next_run(request.schedule_type, request.cron_expression)

        schedule = DBWorkflowSchedule(
            id=uuid4(),
            workflow_id=request.workflow_id,
            user_id=self.user.id,
            schedule_type=request.schedule_type,
            cron_expression=request.cron_expression,
            next_run_at=next_run,
            enabled=True,
            input_data=request.input_data,
            created_at=datetime.utcnow()
        )

        self.db.add(schedule)
        self.db.commit()
        self.db.refresh(schedule)

        return WorkflowSchedule.model_validate(schedule)

    def list_schedules(
        self,
        workflow_id: Optional[UUID] = None
    ) -> List[WorkflowSchedule]:
        """List schedules"""

        query = self.db.query(DBWorkflowSchedule).filter(
            DBWorkflowSchedule.user_id == self.user.id
        )

        if workflow_id:
            query = query.filter(DBWorkflowSchedule.workflow_id == workflow_id)

        schedules = query.all()
        return [WorkflowSchedule.model_validate(s) for s in schedules]

    def delete_schedule(self, schedule_id: UUID) -> bool:
        """Delete schedule"""

        schedule = self.db.query(DBWorkflowSchedule).filter(
            DBWorkflowSchedule.id == schedule_id,
            DBWorkflowSchedule.user_id == self.user.id
        ).first()

        if not schedule:
            return False

        self.db.delete(schedule)
        self.db.commit()
        return True

    # ==================== Validation ====================

    def validate_workflow(self, definition: WorkflowDefinition) -> Dict[str, Any]:
        """Validate workflow definition"""

        errors = []
        warnings = []

        # Check for start node
        start_nodes = [n for n in definition.nodes if n.config.type == "start"]
        if len(start_nodes) == 0:
            errors.append("Workflow must have exactly one START node")
        elif len(start_nodes) > 1:
            errors.append("Workflow can only have one START node")

        # Check for end node
        end_nodes = [n for n in definition.nodes if n.config.type == "end"]
        if len(end_nodes) == 0:
            warnings.append("Workflow should have at least one END node")

        # Check for disconnected nodes
        connected_nodes = set()
        for conn in definition.connections:
            connected_nodes.add(conn.source_node_id)
            connected_nodes.add(conn.target_node_id)

        all_node_ids = {n.id for n in definition.nodes}
        disconnected = all_node_ids - connected_nodes - {n.id for n in start_nodes}

        if disconnected:
            warnings.append(f"{len(disconnected)} node(s) are not connected")

        # Check for invalid connections
        for conn in definition.connections:
            source_exists = any(n.id == conn.source_node_id for n in definition.nodes)
            target_exists = any(n.id == conn.target_node_id for n in definition.nodes)

            if not source_exists:
                errors.append(f"Connection references non-existent source node: {conn.source_node_id}")
            if not target_exists:
                errors.append(f"Connection references non-existent target node: {conn.target_node_id}")

        # Check for cycles (basic check)
        # TODO: Implement proper cycle detection

        valid = len(errors) == 0

        return {
            "valid": valid,
            "errors": errors,
            "warnings": warnings,
            "error_count": len(errors),
            "warning_count": len(warnings)
        }

    # ==================== Helpers ====================

    def _to_response(self, workflow: Workflow) -> WorkflowResponse:
        """Convert DB model to response"""
        return WorkflowResponse(
            id=workflow.id,
            user_id=workflow.user_id,
            name=workflow.name,
            description=workflow.description,
            definition=WorkflowDefinition(**workflow.definition),
            settings=WorkflowSettings(**workflow.settings),
            status=workflow.status,
            tags=workflow.tags or [],
            created_at=workflow.created_at,
            updated_at=workflow.updated_at,
            last_executed_at=workflow.last_executed_at,
            execution_count=workflow.execution_count
        )

    def _execution_to_response(self, execution: WorkflowExecution) -> WorkflowExecutionResponse:
        """Convert execution to response"""

        logs = []
        if execution.logs:
            logs = [ExecutionLogEntry(**log) for log in execution.logs]

        return WorkflowExecutionResponse(
            id=execution.id,
            workflow_id=execution.workflow_id,
            status=execution.status,
            started_at=execution.started_at,
            completed_at=execution.completed_at,
            duration_seconds=execution.duration_seconds,
            output_data=execution.output_data,
            error=execution.error,
            logs=logs
        )

    def _calculate_next_run(
        self,
        schedule_type: ScheduleType,
        cron_expression: Optional[str] = None
    ) -> datetime:
        """Calculate next run time for schedule"""

        from datetime import timedelta

        now = datetime.utcnow()

        if schedule_type == ScheduleType.ONCE:
            return now

        elif schedule_type == ScheduleType.HOURLY:
            return now + timedelta(hours=1)

        elif schedule_type == ScheduleType.DAILY:
            return now + timedelta(days=1)

        elif schedule_type == ScheduleType.WEEKLY:
            return now + timedelta(weeks=1)

        elif schedule_type == ScheduleType.MONTHLY:
            return now + timedelta(days=30)

        elif schedule_type == ScheduleType.CRON:
            # TODO: Implement proper cron parsing
            # For now, default to hourly
            return now + timedelta(hours=1)

        return now
