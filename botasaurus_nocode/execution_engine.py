"""
Workflow Execution Engine
==========================

Executes visual workflows node by node.
"""

import asyncio
import time
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from uuid import UUID, uuid4
import re
import json

from .schemas import (
    WorkflowDefinition, WorkflowNode, NodeConnection, NodeType,
    WorkflowStatus, ExecutionLogEntry, NavigateNodeConfig,
    ClickNodeConfig, TypeTextNodeConfig, WaitNodeConfig,
    ExtractTextNodeConfig, ExtractMultipleNodeConfig,
    TransformNodeConfig, ConditionNodeConfig, LoopNodeConfig,
    SaveJsonNodeConfig, ApiCallNodeConfig, AIExtractNodeConfig
)


class ExecutionContext:
    """Context for workflow execution"""

    def __init__(self, input_data: Optional[Dict[str, Any]] = None):
        self.data: Dict[str, Any] = input_data or {}
        self.logs: List[ExecutionLogEntry] = []
        self.driver: Optional[Any] = None  # Browser driver instance
        self.start_time: datetime = datetime.utcnow()
        self.status: WorkflowStatus = WorkflowStatus.RUNNING
        self.error: Optional[str] = None

    def log(self, node_id: str, node_type: NodeType, status: str,
            message: Optional[str] = None, data: Optional[Dict[str, Any]] = None,
            duration_ms: Optional[int] = None):
        """Add log entry"""
        entry = ExecutionLogEntry(
            timestamp=datetime.utcnow(),
            node_id=node_id,
            node_type=node_type,
            status=status,
            message=message,
            data=data,
            duration_ms=duration_ms
        )
        self.logs.append(entry)

    def set_data(self, key: str, value: Any):
        """Set data in context"""
        self.data[key] = value

    def get_data(self, key: str, default: Any = None) -> Any:
        """Get data from context"""
        return self.data.get(key, default)

    def get_all_data(self) -> Dict[str, Any]:
        """Get all data"""
        return self.data.copy()


class WorkflowExecutionEngine:
    """
    Executes visual workflows.

    Supports:
    - Sequential execution
    - Conditional branching
    - Loops
    - Parallel execution
    - Error handling and retries
    """

    def __init__(self, ai_service=None):
        self.ai_service = ai_service
        self.node_executors: Dict[NodeType, Callable] = {
            NodeType.START: self._execute_start,
            NodeType.END: self._execute_end,
            NodeType.NAVIGATE: self._execute_navigate,
            NodeType.CLICK: self._execute_click,
            NodeType.TYPE_TEXT: self._execute_type_text,
            NodeType.WAIT: self._execute_wait,
            NodeType.EXTRACT_TEXT: self._execute_extract_text,
            NodeType.EXTRACT_MULTIPLE: self._execute_extract_multiple,
            NodeType.TRANSFORM: self._execute_transform,
            NodeType.CONDITION: self._execute_condition,
            NodeType.LOOP: self._execute_loop,
            NodeType.SAVE_JSON: self._execute_save_json,
            NodeType.API_CALL: self._execute_api_call,
            NodeType.AI_EXTRACT: self._execute_ai_extract,
        }

    async def execute(
        self,
        workflow: WorkflowDefinition,
        input_data: Optional[Dict[str, Any]] = None,
        settings: Optional[Any] = None
    ) -> ExecutionContext:
        """
        Execute a workflow.

        Args:
            workflow: Workflow definition
            input_data: Initial data for workflow
            settings: Workflow settings (browser config, etc.)

        Returns:
            ExecutionContext with results and logs
        """
        context = ExecutionContext(input_data)

        # Initialize browser if needed
        if self._needs_browser(workflow):
            try:
                context.driver = await self._init_browser(settings)
            except Exception as e:
                context.status = WorkflowStatus.FAILED
                context.error = f"Failed to initialize browser: {str(e)}"
                return context

        try:
            # Find start node
            start_node = next(
                (n for n in workflow.nodes if n.config.type == NodeType.START),
                None
            )

            if not start_node:
                raise ValueError("No START node found in workflow")

            # Execute from start node
            await self._execute_from_node(
                start_node, workflow, context
            )

            # Mark as completed if no errors
            if context.status == WorkflowStatus.RUNNING:
                context.status = WorkflowStatus.COMPLETED

        except Exception as e:
            context.status = WorkflowStatus.FAILED
            context.error = str(e)
            context.log("error", NodeType.START, "error", f"Workflow failed: {str(e)}")

        finally:
            # Cleanup browser
            if context.driver:
                try:
                    await self._cleanup_browser(context.driver)
                except:
                    pass

        return context

    async def _execute_from_node(
        self,
        node: WorkflowNode,
        workflow: WorkflowDefinition,
        context: ExecutionContext
    ):
        """Execute workflow starting from a specific node"""

        # Skip if disabled
        if not node.config.enabled:
            context.log(node.id, node.config.type, "skipped", "Node is disabled")
            return

        start_time = time.time()

        try:
            # Get executor for this node type
            executor = self.node_executors.get(node.config.type)
            if not executor:
                raise ValueError(f"Unknown node type: {node.config.type}")

            # Execute node with retries
            retry_count = getattr(node.config, 'retry_count', 0)
            retry_delay = getattr(node.config, 'retry_delay', 2)

            for attempt in range(retry_count + 1):
                try:
                    result = await executor(node, context)
                    duration_ms = int((time.time() - start_time) * 1000)
                    context.log(
                        node.id, node.config.type, "success",
                        f"Executed successfully",
                        duration_ms=duration_ms
                    )
                    break
                except Exception as e:
                    if attempt < retry_count:
                        context.log(
                            node.id, node.config.type, "error",
                            f"Attempt {attempt + 1} failed: {str(e)}, retrying..."
                        )
                        await asyncio.sleep(retry_delay)
                    else:
                        raise

            # Find next nodes
            next_nodes = self._get_next_nodes(node, workflow, context)

            # Execute next nodes
            for next_node in next_nodes:
                await self._execute_from_node(next_node, workflow, context)

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            context.log(
                node.id, node.config.type, "error",
                f"Failed: {str(e)}",
                duration_ms=duration_ms
            )
            raise

    def _get_next_nodes(
        self,
        current_node: WorkflowNode,
        workflow: WorkflowDefinition,
        context: ExecutionContext
    ) -> List[WorkflowNode]:
        """Get next nodes to execute based on connections"""

        next_nodes = []

        # Find connections from this node
        connections = [
            c for c in workflow.connections
            if c.source_node_id == current_node.id
        ]

        for conn in connections:
            # Check condition if present
            if conn.condition:
                if not self._evaluate_condition(conn.condition, context):
                    continue

            # Find target node
            target_node = next(
                (n for n in workflow.nodes if n.id == conn.target_node_id),
                None
            )

            if target_node:
                next_nodes.append(target_node)

        return next_nodes

    def _evaluate_condition(self, condition: str, context: ExecutionContext) -> bool:
        """Safely evaluate condition expression"""
        try:
            # Create safe namespace with context data
            namespace = {
                'data': context.data,
                **context.data  # Also allow direct access to keys
            }

            # Evaluate expression
            result = eval(condition, {"__builtins__": {}}, namespace)
            return bool(result)
        except Exception as e:
            context.log("condition", NodeType.CONDITION, "error",
                       f"Condition evaluation failed: {str(e)}")
            return False

    # ==================== Node Executors ====================

    async def _execute_start(self, node: WorkflowNode, context: ExecutionContext):
        """Execute START node"""
        context.log(node.id, NodeType.START, "success", "Workflow started")

    async def _execute_end(self, node: WorkflowNode, context: ExecutionContext):
        """Execute END node"""
        context.log(node.id, NodeType.END, "success", "Workflow completed")

    async def _execute_navigate(self, node: WorkflowNode, context: ExecutionContext):
        """Execute NAVIGATE node"""
        config: NavigateNodeConfig = node.config

        if not context.driver:
            raise ValueError("Browser not initialized")

        # Navigate to URL
        await context.driver.get(config.url)

        # Wait for page load
        if config.wait_until == "networkidle":
            await context.driver.wait_for_network_idle()
        elif config.wait_until == "load":
            await context.driver.wait_for_load()

        context.log(node.id, NodeType.NAVIGATE, "success",
                   f"Navigated to {config.url}")

    async def _execute_click(self, node: WorkflowNode, context: ExecutionContext):
        """Execute CLICK node"""
        config: ClickNodeConfig = node.config

        if not context.driver:
            raise ValueError("Browser not initialized")

        # Wait for element if needed
        if config.wait_for_selector:
            await context.driver.wait_for_element(config.selector)

        # Find and click element
        if config.human_like:
            await context.driver.click(config.selector, human=True)
        else:
            await context.driver.click(config.selector)

        context.log(node.id, NodeType.CLICK, "success",
                   f"Clicked {config.selector}")

    async def _execute_type_text(self, node: WorkflowNode, context: ExecutionContext):
        """Execute TYPE_TEXT node"""
        config: TypeTextNodeConfig = node.config

        if not context.driver:
            raise ValueError("Browser not initialized")

        # Find element
        element = await context.driver.find_element(config.selector)

        # Clear if needed
        if config.clear_first:
            await element.clear()

        # Type text
        if config.human_like:
            await context.driver.type(config.selector, config.text, human=True)
        else:
            await element.send_keys(config.text)

        # Press enter if needed
        if config.press_enter:
            await element.send_keys("\n")

        context.log(node.id, NodeType.TYPE_TEXT, "success",
                   f"Typed into {config.selector}")

    async def _execute_wait(self, node: WorkflowNode, context: ExecutionContext):
        """Execute WAIT node"""
        config: WaitNodeConfig = node.config

        if config.wait_type == "time":
            await asyncio.sleep(config.duration or 1)

        elif config.wait_type == "element" and context.driver:
            await context.driver.wait_for_element(config.selector)

        elif config.wait_type == "navigation" and context.driver:
            await context.driver.wait_for_navigation()

        elif config.wait_type == "network" and context.driver:
            await context.driver.wait_for_network_idle()

        context.log(node.id, NodeType.WAIT, "success",
                   f"Wait completed: {config.wait_type}")

    async def _execute_extract_text(self, node: WorkflowNode, context: ExecutionContext):
        """Execute EXTRACT_TEXT node"""
        config: ExtractTextNodeConfig = node.config

        if not context.driver:
            raise ValueError("Browser not initialized")

        try:
            # Find element and extract text
            element = await context.driver.find_element(config.selector)
            text = await element.text()

            if config.trim:
                text = text.strip()

            # Store in context
            context.set_data(config.output_key, text)

            context.log(node.id, NodeType.EXTRACT_TEXT, "success",
                       f"Extracted: {text[:50]}...")

        except Exception as e:
            # Use default value if provided
            if config.default_value is not None:
                context.set_data(config.output_key, config.default_value)
                context.log(node.id, NodeType.EXTRACT_TEXT, "success",
                           f"Used default value: {config.default_value}")
            else:
                raise

    async def _execute_extract_multiple(self, node: WorkflowNode, context: ExecutionContext):
        """Execute EXTRACT_MULTIPLE node"""
        config: ExtractMultipleNodeConfig = node.config

        if not context.driver:
            raise ValueError("Browser not initialized")

        # Find all container elements
        containers = await context.driver.find_elements(config.container_selector)

        results = []
        for i, container in enumerate(containers):
            if config.limit and i >= config.limit:
                break

            item_data = {}
            for field in config.fields:
                name = field["name"]
                selector = field["selector"]
                attribute = field.get("attribute")

                try:
                    element = await container.find_element(selector)

                    if attribute:
                        value = await element.get_attribute(attribute)
                    else:
                        value = await element.text()

                    item_data[name] = value
                except:
                    item_data[name] = None

            results.append(item_data)

        # Store results
        context.set_data(config.output_key, results)

        context.log(node.id, NodeType.EXTRACT_MULTIPLE, "success",
                   f"Extracted {len(results)} items")

    async def _execute_transform(self, node: WorkflowNode, context: ExecutionContext):
        """Execute TRANSFORM node"""
        config: TransformNodeConfig = node.config

        # Get input data
        input_value = context.get_data(config.input_key)

        # Create safe namespace
        namespace = {
            'value': input_value,
            'data': context.data,
            're': re,
            'json': json,
            'len': len,
            'str': str,
            'int': int,
            'float': float,
            'list': list,
            'dict': dict,
        }

        # Execute transformation
        result = eval(config.expression, {"__builtins__": {}}, namespace)

        # Store result
        context.set_data(config.output_key, result)

        context.log(node.id, NodeType.TRANSFORM, "success",
                   f"Transformed data")

    async def _execute_condition(self, node: WorkflowNode, context: ExecutionContext):
        """Execute CONDITION node"""
        config: ConditionNodeConfig = node.config

        # Condition is evaluated in _get_next_nodes
        # This node just passes through
        context.log(node.id, NodeType.CONDITION, "success",
                   f"Condition evaluated")

    async def _execute_loop(self, node: WorkflowNode, context: ExecutionContext):
        """Execute LOOP node"""
        config: LoopNodeConfig = node.config

        # Get array to loop over
        items = context.get_data(config.input_key, [])

        if not isinstance(items, list):
            raise ValueError(f"Loop input must be array, got {type(items)}")

        # Limit iterations
        max_iter = config.max_iterations or len(items)
        items = items[:max_iter]

        context.log(node.id, NodeType.LOOP, "success",
                   f"Looping over {len(items)} items")

        # TODO: Implement loop body execution
        # For now, just log each item
        for i, item in enumerate(items):
            context.set_data(config.loop_variable, item)
            context.log(node.id, NodeType.LOOP, "success",
                       f"Loop iteration {i + 1}/{len(items)}")

    async def _execute_save_json(self, node: WorkflowNode, context: ExecutionContext):
        """Execute SAVE_JSON node"""
        config: SaveJsonNodeConfig = node.config

        # Get data to save
        if config.data_key:
            data = context.get_data(config.data_key)
        else:
            data = context.get_all_data()

        # Save to file if path provided
        if config.file_path:
            import json
            with open(config.file_path, 'w') as f:
                json.dump(data, f, indent=2)

        # Always store in context as 'output'
        context.set_data('output', data)

        context.log(node.id, NodeType.SAVE_JSON, "success",
                   f"Saved JSON output")

    async def _execute_api_call(self, node: WorkflowNode, context: ExecutionContext):
        """Execute API_CALL node"""
        config: ApiCallNodeConfig = node.config

        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.request(
                method=config.method,
                url=config.url,
                headers=config.headers,
                json=config.body
            ) as response:
                result = await response.json()

        # Store result
        context.set_data(config.output_key, result)

        context.log(node.id, NodeType.API_CALL, "success",
                   f"API call completed: {config.method} {config.url}")

    async def _execute_ai_extract(self, node: WorkflowNode, context: ExecutionContext):
        """Execute AI_EXTRACT node"""
        config: AIExtractNodeConfig = node.config

        if not self.ai_service:
            raise ValueError("AI service not configured")

        # Get page content
        if config.selector and context.driver:
            element = await context.driver.find_element(config.selector)
            html = await element.html()
        elif context.driver:
            html = await context.driver.page_source()
        else:
            raise ValueError("Browser not initialized")

        # Get screenshot if using vision
        screenshot = None
        if config.use_vision and context.driver:
            screenshot = await context.driver.screenshot()

        # Use AI to extract data
        result = await self.ai_service.extract_data(
            prompt=config.prompt,
            html=html,
            screenshot=screenshot if config.use_vision else None
        )

        # Store result
        context.set_data(config.output_key, result)

        context.log(node.id, NodeType.AI_EXTRACT, "success",
                   f"AI extracted data")

    # ==================== Browser Management ====================

    def _needs_browser(self, workflow: WorkflowDefinition) -> bool:
        """Check if workflow needs browser"""
        browser_node_types = {
            NodeType.NAVIGATE, NodeType.CLICK, NodeType.TYPE_TEXT,
            NodeType.EXTRACT_TEXT, NodeType.EXTRACT_MULTIPLE, NodeType.SCREENSHOT
        }

        return any(
            n.config.type in browser_node_types
            for n in workflow.nodes
        )

    async def _init_browser(self, settings):
        """Initialize browser"""
        # TODO: Initialize actual browser (Playwright/Botasaurus)
        # For now, return mock driver
        class MockDriver:
            async def get(self, url): pass
            async def wait_for_element(self, selector): pass
            async def wait_for_network_idle(self): pass
            async def wait_for_load(self): pass
            async def click(self, selector, human=False): pass
            async def type(self, selector, text, human=False): pass
            async def find_element(self, selector): return MockElement()
            async def find_elements(self, selector): return []
            async def page_source(self): return "<html></html>"
            async def screenshot(self): return b""

        class MockElement:
            async def text(self): return ""
            async def html(self): return ""
            async def clear(self): pass
            async def send_keys(self, text): pass
            async def get_attribute(self, attr): return ""
            async def find_element(self, selector): return MockElement()

        return MockDriver()

    async def _cleanup_browser(self, driver):
        """Cleanup browser"""
        # TODO: Implement actual cleanup
        pass
