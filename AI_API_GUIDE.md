# AI Copilot API Guide

Complete guide to using the Botasaurus AI Copilot API for automated scraper generation.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Authentication](#authentication)
3. [REST API Endpoints](#rest-api-endpoints)
4. [WebSocket Streaming](#websocket-streaming)
5. [Code Examples](#code-examples)
6. [Best Practices](#best-practices)

---

## Quick Start

### Starting the Server

```bash
# Install dependencies
pip install -r requirements-platform.txt

# Set environment variables
export OPENAI_API_KEY="your-key-here"
export DATABASE_URL="postgresql://user:pass@localhost/botasaurus"

# Run the server
uvicorn botasaurus_platform.main:app --reload
```

### Access API Documentation

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

---

## Authentication

All AI endpoints require JWT authentication. First, register and login:

### Register

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure_password",
    "name": "Test User"
  }'
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Using the Token

Include the access token in all subsequent requests:

```bash
export TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."

curl -X POST http://localhost:8000/api/ai/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{ "prompt": "..." }'
```

---

## REST API Endpoints

### 1. Generate Scraper

**POST** `/api/ai/generate`

Generate a new scraper from natural language description.

**Request:**
```json
{
  "prompt": "Scrape product names and prices from Amazon search results",
  "url": "https://www.amazon.com/s?k=laptops",
  "use_vision": true,
  "context": {
    "additional_info": "Focus on laptop brands and specifications"
  },
  "conversation_id": null
}
```

**Response:**
```json
{
  "code": "from botasaurus import browser\n\n@browser\ndef scrape_amazon_products(driver, data):\n    \"\"\"Scrape Amazon product listings\"\"\"\n    try:\n        driver.get(data)\n        driver.wait_for_element('.s-result-item', timeout=10)\n        \n        products = []\n        items = driver.find_elements('.s-result-item')\n        \n        for item in items:\n            try:\n                name = item.find_element('h2 a span').text\n                price = item.find_element('.a-price-whole').text\n                \n                products.append({\n                    'name': name,\n                    'price': price\n                })\n            except:\n                continue\n        \n        return products\n    except Exception as e:\n        print(f'Error: {e}')\n        return []",
  "explanation": "This scraper uses browser automation to extract product names and prices from Amazon search results. It waits for products to load, then iterates through each item extracting the name and price.",
  "selectors": [".s-result-item", "h2 a span", ".a-price-whole"],
  "warnings": [],
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "tokens_used": 1247
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/ai/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Scrape product names and prices from Amazon",
    "url": "https://www.amazon.com/s?k=laptops",
    "use_vision": true
  }'
```

---

### 2. Refine Scraper

**POST** `/api/ai/refine`

Improve existing scraper based on feedback.

**Request:**
```json
{
  "current_code": "from botasaurus import browser...",
  "refinement_prompt": "Add error handling and retry logic for failed requests",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response:**
```json
{
  "code": "from botasaurus import browser\nfrom botasaurus.retry import retry\n\n@browser\n@retry(times=3, delay=2)\ndef scrape_amazon_products(driver, data):\n    ...",
  "explanation": "Updated code to include retry decorator and improved error handling",
  "changes": [
    "Added: from botasaurus.retry import retry",
    "Added: @retry(times=3, delay=2)",
    "Added: try-except blocks around selectors"
  ],
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "tokens_used": 823
}
```

---

### 3. Analyze Page

**POST** `/api/ai/analyze-page`

Analyze page structure before generating code.

**Request:**
```json
{
  "url": "https://www.amazon.com/s?k=laptops",
  "use_vision": true
}
```

**Response:**
```json
{
  "page_type": "e-commerce",
  "complexity": "medium",
  "main_content": ["#search", ".s-main-slot"],
  "data_patterns": [
    "Product cards in grid layout",
    "Price elements with .a-price class",
    "Product titles in h2 > a > span"
  ],
  "recommended_selectors": [
    {"type": "title", "selector": "h2 a span"},
    {"type": "price", "selector": ".a-price-whole"},
    {"type": "image", "selector": "img.s-image"}
  ],
  "recommended_approach": "@browser",
  "key_elements": [
    "Search results container",
    "Product cards",
    "Pagination controls"
  ]
}
```

---

### 4. Validate Code

**POST** `/api/ai/validate`

Validate scraper code for syntax, security, and best practices.

**Request:**
```json
{
  "code": "from botasaurus import browser\n\n@browser\ndef scrape(driver, data):\n    driver.get(data)\n    return []",
  "url": "https://example.com"
}
```

**Response:**
```json
{
  "valid": false,
  "errors": [],
  "warnings": [
    "No error handling found - add try/except blocks",
    "No explicit waits found - page might not fully load",
    "Consider using human=True for clicks/typing to avoid detection"
  ],
  "fixable": false,
  "error_count": 0,
  "warning_count": 3
}
```

---

### 5. Conversation Management

#### Create Conversation

**POST** `/api/ai/conversations`

```json
{
  "title": "Amazon Product Scraper",
  "initial_prompt": "Help me scrape Amazon products"
}
```

#### Get All Conversations

**GET** `/api/ai/conversations?limit=50`

Response:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Amazon Product Scraper",
    "messages": [],
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "2025-01-15T10:35:00Z"
  }
]
```

#### Get Specific Conversation

**GET** `/api/ai/conversations/{conversation_id}`

Returns conversation with full message history.

---

### 6. Usage Statistics

**GET** `/api/ai/usage`

Get your AI usage statistics.

**Response:**
```json
{
  "total_tokens": 15420,
  "total_cost": 0.69,
  "requests_count": 12,
  "successful_generations": 10,
  "failed_generations": 2
}
```

---

## WebSocket Streaming

For real-time code generation with progressive updates.

### Connection

**WebSocket URL**: `ws://localhost:8000/api/ai/ws/generate`

### Protocol

**Client sends:**
```json
{
  "action": "generate",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "prompt": "Scrape product data from Amazon",
  "url": "https://www.amazon.com/s?k=laptops",
  "use_vision": true,
  "conversation_id": null
}
```

**Server sends (multiple chunks):**

Status update:
```json
{
  "type": "status",
  "content": "Analyzing page structure..."
}
```

Page analysis:
```json
{
  "type": "analysis",
  "content": "{\"page_type\": \"e-commerce\", ...}"
}
```

Code chunks (streamed):
```json
{"type": "code", "content": "from botasaurus import browser\n\n"}
{"type": "code", "content": "@browser\n"}
{"type": "code", "content": "def scrape(driver, data):\n"}
{"type": "code", "content": "    try:\n"}
...
```

Completion:
```json
{
  "type": "complete",
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "tokens_used": 1500,
  "warnings": [],
  "selectors": [".product-title", ".price"],
  "validation": {
    "valid": true,
    "errors": [],
    "warnings": ["Use human=True for clicks"]
  }
}
```

---

## Code Examples

### Python Client

```python
import requests
import json

class BotasaurusAIClient:
    def __init__(self, base_url="http://localhost:8000", token=None):
        self.base_url = base_url
        self.token = token

    def login(self, email, password):
        """Login and get token"""
        response = requests.post(
            f"{self.base_url}/api/auth/login",
            json={"email": email, "password": password}
        )
        data = response.json()
        self.token = data["access_token"]
        return data

    def generate_scraper(self, prompt, url=None, use_vision=True):
        """Generate scraper from prompt"""
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(
            f"{self.base_url}/api/ai/generate",
            headers=headers,
            json={
                "prompt": prompt,
                "url": url,
                "use_vision": use_vision
            }
        )
        return response.json()

    def refine_scraper(self, code, refinement_prompt, conversation_id):
        """Refine existing scraper"""
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(
            f"{self.base_url}/api/ai/refine",
            headers=headers,
            json={
                "current_code": code,
                "refinement_prompt": refinement_prompt,
                "conversation_id": conversation_id
            }
        )
        return response.json()

    def analyze_page(self, url):
        """Analyze page structure"""
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.post(
            f"{self.base_url}/api/ai/analyze-page",
            headers=headers,
            json={"url": url, "use_vision": True}
        )
        return response.json()

# Usage
client = BotasaurusAIClient()
client.login("user@example.com", "password")

# Generate scraper
result = client.generate_scraper(
    prompt="Scrape product names and prices",
    url="https://www.amazon.com/s?k=laptops"
)

print(result["code"])
print(f"Tokens used: {result['tokens_used']}")

# Refine the scraper
refined = client.refine_scraper(
    code=result["code"],
    refinement_prompt="Add pagination support",
    conversation_id=result["conversation_id"]
)

print(refined["code"])
print(f"Changes: {refined['changes']}")
```

### JavaScript/TypeScript Client

```typescript
class BotasaurusAIClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl = "http://localhost:8000") {
    this.baseUrl = baseUrl;
  }

  async login(email: string, password: string) {
    const response = await fetch(`${this.baseUrl}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });
    const data = await response.json();
    this.token = data.access_token;
    return data;
  }

  async generateScraper(prompt: string, url?: string, useVision = true) {
    const response = await fetch(`${this.baseUrl}/api/ai/generate`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${this.token}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ prompt, url, use_vision: useVision })
    });
    return response.json();
  }

  streamGenerate(prompt: string, url?: string) {
    const ws = new WebSocket(`ws://localhost:8000/api/ai/ws/generate`);

    ws.onopen = () => {
      ws.send(JSON.stringify({
        action: "generate",
        token: this.token,
        prompt,
        url,
        use_vision: true
      }));
    };

    return ws;
  }
}

// Usage
const client = new BotasaurusAIClient();
await client.login("user@example.com", "password");

// Stream generation
const ws = client.streamGenerate(
  "Scrape product data",
  "https://www.amazon.com/s?k=laptops"
);

let fullCode = "";

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === "status") {
    console.log(`Status: ${data.content}`);
  } else if (data.type === "code") {
    fullCode += data.content;
    console.log(data.content);
  } else if (data.type === "complete") {
    console.log("\n=== Generation Complete ===");
    console.log(`Tokens used: ${data.tokens_used}`);
    console.log(`Warnings: ${data.warnings.join(", ")}`);
    console.log(`Full code:\n${fullCode}`);
    ws.close();
  }
};
```

---

## Best Practices

### 1. Use Vision Analysis for Complex Pages

Vision analysis provides more accurate results for:
- Dynamic single-page applications (React, Vue, Angular)
- Complex layouts with nested elements
- Pages with heavy JavaScript rendering

```json
{
  "prompt": "Scrape data from this SPA",
  "url": "https://example.com",
  "use_vision": true  // Recommended for SPAs
}
```

### 2. Provide Context

Include additional context to improve generation:

```json
{
  "prompt": "Scrape product data",
  "url": "https://example.com",
  "context": {
    "data_format": "Need JSON with name, price, description",
    "pagination": "Has 50 pages of results",
    "auth_required": false
  }
}
```

### 3. Use Conversations for Iterative Refinement

Keep conversation_id to maintain context:

```python
# Initial generation
result1 = client.generate_scraper(prompt="Scrape products")
conv_id = result1["conversation_id"]

# Refinements maintain context
result2 = client.refine_scraper(
    result1["code"],
    "Add error handling",
    conv_id
)

result3 = client.refine_scraper(
    result2["code"],
    "Add pagination",
    conv_id
)
```

### 4. Validate Before Execution

Always validate generated code:

```python
result = client.generate_scraper(prompt="...")
validation = client.validate_code(result["code"])

if validation["valid"]:
    # Safe to execute
    exec(result["code"])
else:
    print(f"Errors: {validation['errors']}")
    # Request refinement or fix manually
```

### 5. Monitor Usage

Track your token usage to manage costs:

```python
stats = client.get_usage_stats()
print(f"Total cost: ${stats['total_cost']:.2f}")
print(f"Tokens used: {stats['total_tokens']:,}")
```

### 6. Use WebSocket for Better UX

For frontend applications, use WebSocket streaming to show real-time progress:

```javascript
const ws = client.streamGenerate(prompt, url);

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  switch(data.type) {
    case "status":
      updateStatusBar(data.content);
      break;
    case "code":
      appendCodeToEditor(data.content);
      break;
    case "complete":
      showCompletionMessage(data);
      break;
  }
};
```

---

## Error Handling

### Common Errors

**401 Unauthorized**
```json
{
  "error": "Invalid or expired token",
  "status_code": 401
}
```
Solution: Re-authenticate

**429 Rate Limited**
```json
{
  "error": "Rate limit exceeded",
  "status_code": 429
}
```
Solution: Wait or upgrade plan

**500 Generation Failed**
```json
{
  "error": "Generation failed: OpenAI API error",
  "status_code": 500
}
```
Solution: Check LLM API key, retry with different prompt

---

## Support

- **Documentation**: http://localhost:8000/api/docs
- **GitHub Issues**: https://github.com/omkarcloud/botasaurus/issues
- **Discord**: [Coming soon]

---

## Next Steps

1. Try the interactive API documentation at `/api/docs`
2. Generate your first scraper using the Python client
3. Explore conversation management for iterative refinement
4. Monitor your usage statistics
5. Integrate WebSocket streaming into your frontend

Happy scraping! 🤖
