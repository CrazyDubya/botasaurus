"""
No-Code Workflow Schemas
=========================

Pydantic models for visual workflow builder.
"""

from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from uuid import UUID
from datetime import datetime
from enum import Enum


# ==================== Enums ====================

class NodeType(str, Enum):
    """Types of workflow nodes"""
    # Navigation
    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE_TEXT = "type_text"
    WAIT = "wait"

    # Data Extraction
    EXTRACT_TEXT = "extract_text"
    EXTRACT_ATTRIBUTE = "extract_attribute"
    EXTRACT_MULTIPLE = "extract_multiple"
    SCREENSHOT = "screenshot"

    # Data Transformation
    TRANSFORM = "transform"
    FILTER = "filter"
    MAP = "map"
    MERGE = "merge"

    # Control Flow
    CONDITION = "condition"
    LOOP = "loop"
    PARALLEL = "parallel"

    # Data Output
    SAVE_JSON = "save_json"
    SAVE_CSV = "save_csv"
    API_CALL = "api_call"
    DATABASE = "database"

    # AI-Powered
    AI_EXTRACT = "ai_extract"
    AI_CLASSIFY = "ai_classify"
    AI_GENERATE = "ai_generate"

    # Special
    START = "start"
    END = "end"


class WorkflowStatus(str, Enum):
    """Workflow execution status"""
    DRAFT = "draft"
    ACTIVE = "active"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ScheduleType(str, Enum):
    """Schedule types for workflows"""
    ONCE = "once"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CRON = "cron"


class BrowserType(str, Enum):
    """Browser type for scraping"""
    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"


# ==================== Node Configuration Models ====================

class NodePosition(BaseModel):
    """Position of node on canvas"""
    x: float
    y: float


class NodeConnection(BaseModel):
    """Connection between nodes"""
    source_node_id: str = Field(..., description="Source node ID")
    source_handle: str = Field(default="output", description="Source handle ID")
    target_node_id: str = Field(..., description="Target node ID")
    target_handle: str = Field(default="input", description="Target handle ID")
    condition: Optional[str] = Field(None, description="Condition for connection (for conditional flows)")


class BaseNodeConfig(BaseModel):
    """Base configuration for all nodes"""
    type: NodeType
    label: Optional[str] = None
    description: Optional[str] = None
    enabled: bool = True
    timeout: Optional[int] = Field(None, description="Timeout in seconds")
    retry_count: int = Field(0, description="Number of retries on failure")
    retry_delay: int = Field(2, description="Delay between retries in seconds")


class NavigateNodeConfig(BaseNodeConfig):
    """Navigate to URL"""
    type: NodeType = NodeType.NAVIGATE
    url: str = Field(..., description="URL to navigate to")
    wait_until: str = Field("networkidle", description="Wait condition: load|networkidle|domcontentloaded")


class ClickNodeConfig(BaseNodeConfig):
    """Click an element"""
    type: NodeType = NodeType.CLICK
    selector: str = Field(..., description="CSS selector or XPath")
    selector_type: str = Field("css", description="css|xpath")
    wait_for_selector: bool = True
    human_like: bool = Field(True, description="Use human-like clicking")


class TypeTextNodeConfig(BaseNodeConfig):
    """Type text into an element"""
    type: NodeType = NodeType.TYPE_TEXT
    selector: str = Field(..., description="CSS selector or XPath")
    text: str = Field(..., description="Text to type")
    clear_first: bool = True
    press_enter: bool = False
    human_like: bool = Field(True, description="Use human-like typing")


class WaitNodeConfig(BaseNodeConfig):
    """Wait for condition"""
    type: NodeType = NodeType.WAIT
    wait_type: str = Field("time", description="time|element|navigation|network")
    duration: Optional[int] = Field(None, description="Duration in seconds (for time wait)")
    selector: Optional[str] = Field(None, description="Selector to wait for (for element wait)")


class ExtractTextNodeConfig(BaseNodeConfig):
    """Extract text from element"""
    type: NodeType = NodeType.EXTRACT_TEXT
    selector: str = Field(..., description="CSS selector or XPath")
    output_key: str = Field(..., description="Key to store extracted data")
    trim: bool = True
    default_value: Optional[str] = None


class ExtractMultipleNodeConfig(BaseNodeConfig):
    """Extract multiple elements"""
    type: NodeType = NodeType.EXTRACT_MULTIPLE
    container_selector: str = Field(..., description="Container selector")
    fields: List[Dict[str, str]] = Field(..., description="Fields to extract: [{name, selector, attribute?}]")
    output_key: str = Field(..., description="Key to store array of results")
    limit: Optional[int] = None


class TransformNodeConfig(BaseNodeConfig):
    """Transform data using Python expression"""
    type: NodeType = NodeType.TRANSFORM
    expression: str = Field(..., description="Python expression to transform data")
    input_key: str = Field(..., description="Input data key")
    output_key: str = Field(..., description="Output data key")


class ConditionNodeConfig(BaseNodeConfig):
    """Conditional branching"""
    type: NodeType = NodeType.CONDITION
    condition: str = Field(..., description="Python expression returning bool")
    input_key: Optional[str] = None


class LoopNodeConfig(BaseNodeConfig):
    """Loop over data"""
    type: NodeType = NodeType.LOOP
    input_key: str = Field(..., description="Array to loop over")
    loop_variable: str = Field("item", description="Variable name for each item")
    max_iterations: Optional[int] = Field(None, description="Max iterations (safety limit)")


class SaveJsonNodeConfig(BaseNodeConfig):
    """Save data as JSON"""
    type: NodeType = NodeType.SAVE_JSON
    file_path: Optional[str] = Field(None, description="File path (optional)")
    data_key: Optional[str] = Field(None, description="Key to save (or entire context)")


class ApiCallNodeConfig(BaseNodeConfig):
    """Make API call"""
    type: NodeType = NodeType.API_CALL
    url: str
    method: str = Field("GET", description="HTTP method")
    headers: Optional[Dict[str, str]] = None
    body: Optional[Dict[str, Any]] = None
    output_key: str = Field(..., description="Key to store response")


class AIExtractNodeConfig(BaseNodeConfig):
    """AI-powered data extraction"""
    type: NodeType = NodeType.AI_EXTRACT
    prompt: str = Field(..., description="What to extract")
    selector: Optional[str] = Field(None, description="Limit extraction to element")
    output_key: str = Field(..., description="Key to store extracted data")
    use_vision: bool = True


# Union of all node configs
NodeConfig = Union[
    NavigateNodeConfig,
    ClickNodeConfig,
    TypeTextNodeConfig,
    WaitNodeConfig,
    ExtractTextNodeConfig,
    ExtractMultipleNodeConfig,
    TransformNodeConfig,
    ConditionNodeConfig,
    LoopNodeConfig,
    SaveJsonNodeConfig,
    ApiCallNodeConfig,
    AIExtractNodeConfig,
    BaseNodeConfig
]


# ==================== Workflow Models ====================

class WorkflowNode(BaseModel):
    """A node in the workflow"""
    id: str = Field(..., description="Unique node ID")
    config: NodeConfig = Field(..., description="Node configuration")
    position: NodePosition

    class Config:
        use_enum_values = True


class WorkflowDefinition(BaseModel):
    """Complete workflow definition"""
    nodes: List[WorkflowNode] = Field(..., description="All nodes in workflow")
    connections: List[NodeConnection] = Field(..., description="Connections between nodes")

    @validator('nodes')
    def validate_start_node(cls, nodes):
        """Ensure workflow has a start node"""
        start_nodes = [n for n in nodes if n.config.type == NodeType.START]
        if len(start_nodes) == 0:
            raise ValueError("Workflow must have exactly one START node")
        if len(start_nodes) > 1:
            raise ValueError("Workflow can only have one START node")
        return nodes


class WorkflowSettings(BaseModel):
    """Global workflow settings"""
    browser_type: BrowserType = BrowserType.CHROMIUM
    headless: bool = True
    user_agent: Optional[str] = None
    proxy: Optional[str] = None
    timeout: int = Field(30, description="Default timeout in seconds")
    max_retries: int = 3
    anti_detection: bool = Field(True, description="Use anti-detection measures")
    save_screenshots: bool = Field(False, description="Save screenshots on errors")


# ==================== Request/Response Models ====================

class CreateWorkflowRequest(BaseModel):
    """Request to create workflow"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    definition: WorkflowDefinition
    settings: WorkflowSettings = WorkflowSettings()
    tags: List[str] = Field(default_factory=list)


class UpdateWorkflowRequest(BaseModel):
    """Request to update workflow"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    definition: Optional[WorkflowDefinition] = None
    settings: Optional[WorkflowSettings] = None
    tags: Optional[List[str]] = None
    status: Optional[WorkflowStatus] = None


class ExecuteWorkflowRequest(BaseModel):
    """Request to execute workflow"""
    input_data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Initial data")
    settings_override: Optional[WorkflowSettings] = None


class WorkflowResponse(BaseModel):
    """Workflow response"""
    id: UUID
    user_id: UUID
    name: str
    description: Optional[str]
    definition: WorkflowDefinition
    settings: WorkflowSettings
    status: WorkflowStatus
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    last_executed_at: Optional[datetime]
    execution_count: int

    class Config:
        from_attributes = True


class ExecutionLogEntry(BaseModel):
    """Single execution log entry"""
    timestamp: datetime
    node_id: str
    node_type: NodeType
    status: str = Field(..., description="success|error|skipped")
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    duration_ms: Optional[int] = None


class WorkflowExecutionResponse(BaseModel):
    """Workflow execution result"""
    id: UUID
    workflow_id: UUID
    status: WorkflowStatus
    started_at: datetime
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]
    output_data: Optional[Dict[str, Any]]
    error: Optional[str]
    logs: List[ExecutionLogEntry]

    class Config:
        from_attributes = True


# ==================== Template Models ====================

class WorkflowTemplate(BaseModel):
    """Pre-built workflow template"""
    id: str
    name: str
    description: str
    category: str = Field(..., description="e-commerce|news|social|data|general")
    tags: List[str]
    difficulty: str = Field(..., description="beginner|intermediate|advanced")
    estimated_time: str = Field(..., description="e.g., '2 minutes'")
    preview_image: Optional[str] = None
    definition: WorkflowDefinition
    settings: WorkflowSettings
    example_output: Optional[Dict[str, Any]] = None


class TemplateCategory(BaseModel):
    """Category of templates"""
    id: str
    name: str
    description: str
    icon: str
    template_count: int


# ==================== Schedule Models ====================

class WorkflowSchedule(BaseModel):
    """Workflow execution schedule"""
    id: UUID
    workflow_id: UUID
    schedule_type: ScheduleType
    cron_expression: Optional[str] = Field(None, description="Cron expression for custom schedules")
    next_run_at: Optional[datetime]
    last_run_at: Optional[datetime]
    enabled: bool = True
    input_data: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class CreateScheduleRequest(BaseModel):
    """Request to create schedule"""
    workflow_id: UUID
    schedule_type: ScheduleType
    cron_expression: Optional[str] = None
    input_data: Optional[Dict[str, Any]] = None

    @validator('cron_expression')
    def validate_cron(cls, v, values):
        """Validate cron expression if schedule type is CRON"""
        if values.get('schedule_type') == ScheduleType.CRON and not v:
            raise ValueError("cron_expression required for CRON schedule type")
        return v


# ==================== Statistics ====================

class WorkflowStatistics(BaseModel):
    """Workflow statistics"""
    total_executions: int
    successful_executions: int
    failed_executions: int
    average_duration_seconds: float
    last_execution_status: Optional[WorkflowStatus]
    last_execution_at: Optional[datetime]
    success_rate: float = Field(..., description="Percentage 0-100")


class NodeTypeInfo(BaseModel):
    """Information about a node type"""
    type: NodeType
    name: str
    description: str
    category: str = Field(..., description="navigation|extraction|transformation|control|output|ai")
    icon: str
    color: str
    config_schema: Dict[str, Any] = Field(..., description="JSON schema for configuration")
    example_config: Dict[str, Any]
