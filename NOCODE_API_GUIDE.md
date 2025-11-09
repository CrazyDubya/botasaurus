# No-Code Visual Builder API Guide

Complete guide to using the Botasaurus No-Code Visual Workflow Builder API.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Workflow Concepts](#workflow-concepts)
3. [Node Types](#node-types)
4. [REST API Endpoints](#rest-api-endpoints)
5. [Templates](#templates)
6. [Code Examples](#code-examples)
7. [Best Practices](#best-practices)

---

## Quick Start

### Create Your First Workflow

```bash
# 1. Authenticate
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

export TOKEN="your-access-token"

# 2. Create a workflow
curl -X POST http://localhost:8000/api/workflows \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @workflow.json

# 3. Execute it
curl -X POST http://localhost:8000/api/workflows/{workflow_id}/execute \
  -H "Authorization: Bearer $TOKEN" \
  -d '{}'
```

---

## Workflow Concepts

### Workflow Structure

A workflow consists of:
- **Nodes**: Individual actions (navigate, extract, transform, etc.)
- **Connections**: Links between nodes defining the execution flow
- **Settings**: Global configuration (browser type, timeout, etc.)

### Node Types

Workflows support 20+ node types organized into 6 categories:

| Category | Node Types |
|----------|------------|
| **Navigation** | Navigate, Click, Type Text, Wait |
| **Extraction** | Extract Text, Extract Multiple, Extract Attribute, Screenshot |
| **Transformation** | Transform, Filter, Map, Merge |
| **Control Flow** | Condition, Loop, Parallel |
| **Output** | Save JSON, Save CSV, API Call, Database |
| **AI-Powered** | AI Extract, AI Classify, AI Generate |

### Execution Flow

1. Start from **START** node
2. Follow **connections** to next nodes
3. Execute each node in sequence
4. Handle errors with retries
5. Complete at **END** node

---

## Node Types

### Navigation Nodes

#### Navigate
Navigate to a URL.

```json
{
  "id": "nav1",
  "config": {
    "type": "navigate",
    "label": "Go to Homepage",
    "url": "https://example.com",
    "wait_until": "networkidle",
    "timeout": 30,
    "retry_count": 3
  },
  "position": {"x": 100, "y": 200}
}
```

**Parameters**:
- `url` (required): URL to navigate to
- `wait_until`: `load` | `networkidle` | `domcontentloaded`
- `timeout`: Max wait time in seconds
- `retry_count`: Retries on failure

#### Click
Click an element.

```json
{
  "config": {
    "type": "click",
    "label": "Click Search Button",
    "selector": "button.search",
    "selector_type": "css",
    "wait_for_selector": true,
    "human_like": true
  }
}
```

**Parameters**:
- `selector` (required): CSS selector or XPath
- `selector_type`: `css` | `xpath`
- `human_like`: Use human-like clicking (anti-detection)
- `wait_for_selector`: Wait for element to appear

#### Type Text
Type text into an input field.

```json
{
  "config": {
    "type": "type_text",
    "label": "Search for Laptops",
    "selector": "input#search",
    "text": "gaming laptops",
    "clear_first": true,
    "press_enter": true,
    "human_like": true
  }
}
```

**Parameters**:
- `selector` (required): Input field selector
- `text` (required): Text to type
- `clear_first`: Clear field before typing
- `press_enter`: Press Enter after typing
- `human_like`: Use human-like typing

#### Wait
Wait for a condition.

```json
{
  "config": {
    "type": "wait",
    "label": "Wait for Results",
    "wait_type": "element",
    "selector": ".search-results",
    "duration": 5
  }
}
```

**Wait Types**:
- `time`: Wait for duration (seconds)
- `element`: Wait for element to appear
- `navigation`: Wait for navigation to complete
- `network`: Wait for network to be idle

### Extraction Nodes

#### Extract Text
Extract text from a single element.

```json
{
  "config": {
    "type": "extract_text",
    "label": "Get Page Title",
    "selector": "h1.title",
    "output_key": "page_title",
    "trim": true,
    "default_value": "Untitled"
  }
}
```

**Parameters**:
- `selector` (required): Element selector
- `output_key` (required): Variable name to store result
- `trim`: Remove whitespace
- `default_value`: Fallback if extraction fails

#### Extract Multiple
Extract data from multiple elements.

```json
{
  "config": {
    "type": "extract_multiple",
    "label": "Extract Products",
    "container_selector": ".product-card",
    "fields": [
      {"name": "title", "selector": ".product-title"},
      {"name": "price", "selector": ".price"},
      {"name": "rating", "selector": ".rating"},
      {"name": "image", "selector": "img", "attribute": "src"},
      {"name": "link", "selector": "a", "attribute": "href"}
    ],
    "output_key": "products",
    "limit": 50
  }
}
```

**Parameters**:
- `container_selector` (required): Container element (e.g., product card)
- `fields` (required): Array of fields to extract
  - `name`: Field name
  - `selector`: Element selector within container
  - `attribute` (optional): Extract attribute instead of text
- `output_key` (required): Variable name for results array
- `limit` (optional): Max number of items to extract

### Transformation Nodes

#### Transform
Transform data using Python expressions.

```json
{
  "config": {
    "type": "transform",
    "label": "Parse Price",
    "input_key": "price",
    "output_key": "price_numeric",
    "expression": "float(value.replace('$', '').replace(',', ''))"
  }
}
```

**Safe Operations**:
- String methods: `str.replace()`, `str.strip()`, `str.split()`
- Math: `int()`, `float()`, `len()`
- Regex: `re.match()`, `re.search()`
- JSON: `json.loads()`, `json.dumps()`

**Parameters**:
- `input_key`: Source data variable
- `output_key`: Destination variable
- `expression`: Python expression to transform data

### Control Flow Nodes

#### Condition
Conditional branching.

```json
{
  "config": {
    "type": "condition",
    "label": "Check if Results Found",
    "condition": "len(products) > 0",
    "input_key": "products"
  }
}
```

Then create connections with conditions:
```json
{
  "source_node_id": "condition1",
  "target_node_id": "process_results",
  "condition": "True"
},
{
  "source_node_id": "condition1",
  "target_node_id": "no_results_handler",
  "condition": "False"
}
```

#### Loop
Iterate over an array.

```json
{
  "config": {
    "type": "loop",
    "label": "Process Each Product",
    "input_key": "products",
    "loop_variable": "product",
    "max_iterations": 100
  }
}
```

### Output Nodes

#### Save JSON
Save data to JSON.

```json
{
  "config": {
    "type": "save_json",
    "label": "Save Results",
    "data_key": "products",
    "file_path": "/path/to/output.json"
  }
}
```

#### API Call
Make HTTP requests.

```json
{
  "config": {
    "type": "api_call",
    "label": "Send to Webhook",
    "url": "https://webhook.site/unique-id",
    "method": "POST",
    "headers": {"Content-Type": "application/json"},
    "body": {"data": "{{products}}"},
    "output_key": "api_response"
  }
}
```

### AI-Powered Nodes

#### AI Extract
Use AI to extract unstructured data.

```json
{
  "config": {
    "type": "ai_extract",
    "label": "Extract with AI",
    "prompt": "Extract product specifications as JSON with keys: brand, model, cpu, ram, storage",
    "selector": ".product-details",
    "use_vision": true,
    "output_key": "specs"
  }
}
```

---

## REST API Endpoints

### Workflow Management

#### POST /api/workflows
Create a new workflow.

**Request**:
```json
{
  "name": "Amazon Product Scraper",
  "description": "Scrape Amazon product listings",
  "definition": {
    "nodes": [...],
    "connections": [...]
  },
  "settings": {
    "browser_type": "chromium",
    "headless": true,
    "timeout": 30,
    "max_retries": 3,
    "anti_detection": true
  },
  "tags": ["e-commerce", "amazon"]
}
```

**Response**: `WorkflowResponse` with `id`

#### GET /api/workflows
List all workflows.

**Query Parameters**:
- `status`: Filter by status (draft|active|completed|failed)
- `tags`: Comma-separated tags
- `limit`: Results per page (1-100)
- `offset`: Pagination offset

#### GET /api/workflows/{id}
Get workflow by ID.

#### PUT /api/workflows/{id}
Update workflow.

**Request** (all fields optional):
```json
{
  "name": "Updated Name",
  "description": "New description",
  "definition": {...},
  "settings": {...},
  "tags": ["new", "tags"],
  "status": "active"
}
```

#### DELETE /api/workflows/{id}
Delete workflow.

#### POST /api/workflows/{id}/duplicate
Duplicate existing workflow.

### Execution

#### POST /api/workflows/{id}/execute
Execute a workflow.

**Request**:
```json
{
  "input_data": {
    "url": "https://www.amazon.com/s?k=laptops",
    "max_results": 50
  },
  "settings_override": {
    "headless": false
  }
}
```

**Response**:
```json
{
  "id": "execution-uuid",
  "workflow_id": "workflow-uuid",
  "status": "completed",
  "started_at": "2025-01-15T10:00:00Z",
  "completed_at": "2025-01-15T10:02:30Z",
  "duration_seconds": 150.5,
  "output_data": {
    "products": [...],
    "count": 50
  },
  "error": null,
  "logs": [
    {
      "timestamp": "2025-01-15T10:00:01Z",
      "node_id": "nav1",
      "node_type": "navigate",
      "status": "success",
      "message": "Navigated to https://...",
      "duration_ms": 1200
    },
    ...
  ]
}
```

#### GET /api/workflows/{id}/executions
List executions for a workflow.

#### GET /api/workflows/executions/{execution_id}
Get execution details.

#### GET /api/workflows/executions
List all user's executions.

### Statistics

#### GET /api/workflows/{id}/statistics
Get workflow statistics.

**Response**:
```json
{
  "total_executions": 42,
  "successful_executions": 38,
  "failed_executions": 4,
  "average_duration_seconds": 145.2,
  "last_execution_status": "completed",
  "last_execution_at": "2025-01-15T10:00:00Z",
  "success_rate": 90.48
}
```

### Scheduling

#### POST /api/workflows/{id}/schedules
Create execution schedule.

**Request**:
```json
{
  "workflow_id": "uuid",
  "schedule_type": "daily",
  "cron_expression": null,
  "input_data": {"url": "..."}
}
```

**Schedule Types**:
- `once`: Run once
- `hourly`: Every hour
- `daily`: Every day
- `weekly`: Every week
- `monthly`: Every month
- `cron`: Custom cron expression

#### GET /api/workflows/{id}/schedules
List schedules for workflow.

#### DELETE /api/workflows/schedules/{schedule_id}
Delete schedule.

### Validation

#### POST /api/workflows/validate
Validate workflow definition without saving.

**Request**: Workflow definition

**Response**:
```json
{
  "valid": true,
  "errors": [],
  "warnings": ["2 node(s) are not connected"],
  "error_count": 0,
  "warning_count": 1
}
```

---

## Templates

### List Templates

```bash
GET /api/templates
GET /api/templates?category=e-commerce
```

### Available Templates

1. **Product Listing Scraper** (`product-listing`)
   - Category: E-Commerce
   - Scrapes product listings with title, price, image, link

2. **Product Details Scraper** (`product-details`)
   - Category: E-Commerce
   - Extracts detailed product information

3. **News Articles Scraper** (`news-articles`)
   - Category: News
   - Scrapes headlines, summaries, authors, dates

4. **Social Media Profile** (`social-profile`)
   - Category: Social
   - Extracts posts from social profiles

5. **HTML Table Scraper** (`table-scraper`)
   - Category: Data
   - Extracts data from HTML tables

### Use Template

```bash
# Get template
GET /api/templates/{template_id}

# Create workflow from template
POST /api/templates/{template_id}/create?name=My Custom Name
```

---

## Code Examples

### Python Client

```python
import requests

class WorkflowClient:
    def __init__(self, base_url="http://localhost:8000", token=None):
        self.base_url = base_url
        self.token = token

    def create_workflow(self, name, definition, settings=None):
        """Create new workflow"""
        response = requests.post(
            f"{self.base_url}/api/workflows",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "name": name,
                "definition": definition,
                "settings": settings or {}
            }
        )
        return response.json()

    def execute_workflow(self, workflow_id, input_data=None):
        """Execute workflow"""
        response = requests.post(
            f"{self.base_url}/api/workflows/{workflow_id}/execute",
            headers={"Authorization": f"Bearer {self.token}"},
            json={"input_data": input_data or {}}
        )
        return response.json()

    def list_templates(self, category=None):
        """List workflow templates"""
        url = f"{self.base_url}/api/templates"
        if category:
            url += f"?category={category}"
        response = requests.get(
            url,
            headers={"Authorization": f"Bearer {self.token}"}
        )
        return response.json()

    def create_from_template(self, template_id, name=None):
        """Create workflow from template"""
        url = f"{self.base_url}/api/templates/{template_id}/create"
        if name:
            url += f"?name={name}"
        response = requests.post(
            url,
            headers={"Authorization": f"Bearer {self.token}"}
        )
        return response.json()

# Usage
client = WorkflowClient(token="your-token")

# List templates
templates = client.list_templates(category="e-commerce")
print(f"Found {len(templates)} templates")

# Create workflow from template
workflow = client.create_from_template(
    template_id="product-listing",
    name="My Amazon Scraper"
)
print(f"Created workflow: {workflow['id']}")

# Execute it
execution = client.execute_workflow(
    workflow['id'],
    input_data={"url": "https://www.amazon.com/s?k=laptops"}
)
print(f"Execution status: {execution['status']}")
print(f"Output: {execution['output_data']}")
```

### JavaScript/TypeScript Client

```typescript
class WorkflowClient {
  constructor(
    private baseUrl = "http://localhost:8000",
    private token: string | null = null
  ) {}

  async createWorkflow(name: string, definition: any, settings?: any) {
    const response = await fetch(`${this.baseUrl}/api/workflows`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${this.token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ name, definition, settings: settings || {} })
    });
    return response.json();
  }

  async executeWorkflow(workflowId: string, inputData?: any) {
    const response = await fetch(
      `${this.baseUrl}/api/workflows/${workflowId}/execute`,
      {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${this.token}`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ input_data: inputData || {} })
      }
    );
    return response.json();
  }

  async getExecutionStatus(executionId: string) {
    const response = await fetch(
      `${this.baseUrl}/api/workflows/executions/${executionId}`,
      {
        headers: { "Authorization": `Bearer ${this.token}` }
      }
    );
    return response.json();
  }

  async listTemplates(category?: string) {
    let url = `${this.baseUrl}/api/templates`;
    if (category) url += `?category=${category}`;

    const response = await fetch(url, {
      headers: { "Authorization": `Bearer ${this.token}` }
    });
    return response.json();
  }

  async createFromTemplate(templateId: string, name?: string) {
    let url = `${this.baseUrl}/api/templates/${templateId}/create`;
    if (name) url += `?name=${encodeURIComponent(name)}`;

    const response = await fetch(url, {
      method: "POST",
      headers: { "Authorization": `Bearer ${this.token}` }
    });
    return response.json();
  }
}

// Usage
const client = new WorkflowClient("http://localhost:8000", "your-token");

// Create from template
const workflow = await client.createFromTemplate(
  "product-listing",
  "My Scraper"
);

// Execute
const execution = await client.executeWorkflow(workflow.id, {
  url: "https://www.amazon.com/s?k=laptops"
});

// Poll for completion
while (execution.status === "running") {
  await new Promise(r => setTimeout(r, 2000));
  execution = await client.getExecutionStatus(execution.id);
}

console.log("Results:", execution.output_data);
```

---

## Best Practices

### 1. Use Templates as Starting Points

Start with a template and customize:

```bash
# Create from template
curl -X POST "http://localhost:8000/api/templates/product-listing/create?name=My Scraper" \
  -H "Authorization: Bearer $TOKEN"

# Get the workflow
curl http://localhost:8000/api/workflows/{id} \
  -H "Authorization: Bearer $TOKEN"

# Modify and update
curl -X PUT http://localhost:8000/api/workflows/{id} \
  -H "Authorization: Bearer $TOKEN" \
  -d @modified-workflow.json
```

### 2. Test Before Scheduling

Always test workflows before creating schedules:

```bash
# Test execution
curl -X POST http://localhost:8000/api/workflows/{id}/execute \
  -H "Authorization: Bearer $TOKEN"

# Check results
curl http://localhost:8000/api/workflows/executions/{execution_id} \
  -H "Authorization: Bearer $TOKEN"

# If successful, create schedule
curl -X POST http://localhost:8000/api/workflows/{id}/schedules \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"schedule_type": "daily"}'
```

### 3. Use Retries and Timeouts

Configure retries for unreliable operations:

```json
{
  "config": {
    "type": "navigate",
    "url": "...",
    "timeout": 30,
    "retry_count": 3,
    "retry_delay": 2
  }
}
```

### 4. Handle Errors Gracefully

Use default values for extractions:

```json
{
  "config": {
    "type": "extract_text",
    "selector": ".price",
    "output_key": "price",
    "default_value": "N/A"
  }
}
```

### 5. Monitor Performance

Check workflow statistics regularly:

```bash
curl http://localhost:8000/api/workflows/{id}/statistics \
  -H "Authorization: Bearer $TOKEN"
```

### 6. Use Anti-Detection

Enable anti-detection for public websites:

```json
{
  "settings": {
    "anti_detection": true,
    "headless": true,
    "browser_type": "chromium"
  }
}
```

### 7. Limit Extractions

Use limits to prevent memory issues:

```json
{
  "config": {
    "type": "extract_multiple",
    "container_selector": ".item",
    "fields": [...],
    "limit": 100
  }
}
```

### 8. Validate Before Executing

Always validate workflows:

```bash
curl -X POST http://localhost:8000/api/workflows/validate \
  -H "Authorization: Bearer $TOKEN" \
  -d @workflow-definition.json
```

---

## Support

- **API Documentation**: http://localhost:8000/api/docs
- **GitHub Issues**: https://github.com/omkarcloud/botasaurus/issues
- **Examples**: See templates at `/api/templates`

---

## Next Steps

1. Explore available templates at `/api/templates`
2. Create your first workflow from a template
3. Test execution with sample data
4. Customize the workflow for your needs
5. Set up schedules for automatic execution
6. Monitor execution statistics

Happy building! 🚀
