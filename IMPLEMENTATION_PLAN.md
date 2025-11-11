# 🚀 Botasaurus Platform - Detailed Implementation Plan

**Version:** 1.0
**Created:** 2025-11-06
**Status:** 🟢 Active Development

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Phase 1: Foundation (Weeks 1-12)](#phase-1-foundation-weeks-1-12)
3. [Phase 2: AI Copilot MVP (Weeks 13-20)](#phase-2-ai-copilot-mvp-weeks-13-20)
4. [Phase 3: No-Code Builder (Weeks 21-32)](#phase-3-no-code-builder-weeks-21-32)
5. [Phase 4: API Marketplace (Weeks 33-44)](#phase-4-api-marketplace-weeks-33-44)
6. [Phase 5: Data Pipelines (Weeks 45-56)](#phase-5-data-pipelines-weeks-45-56)
7. [Phase 6: Polish & Launch (Weeks 57-64)](#phase-6-polish--launch-weeks-57-64)
8. [Development Standards](#development-standards)
9. [Success Metrics](#success-metrics)

---

## Overview

### Mission
Transform Botasaurus from a web scraping framework into an intelligent automation platform with AI-powered features, generating $300K MRR by end of 2025.

### Timeline
- **Total Duration:** 64 weeks (~15 months)
- **Start Date:** Q1 2025
- **Launch Date:** Q2 2026
- **Team Size:** 6-8 people (scaling to 12-15 by end)

### Priorities
1. **Foundation First:** Auth, billing, database schema
2. **AI Copilot:** Differentiation feature
3. **No-Code Builder:** Market expansion
4. **Monetization:** API marketplace, subscriptions
5. **Polish:** UX, documentation, support

---

## Phase 1: Foundation (Weeks 1-12)

**Goal:** Build the infrastructure needed for all other features

**Team:** 4 engineers (2 backend, 1 frontend, 1 devops), 1 PM, 1 designer

### Sprint 1 (Weeks 1-2): Project Setup

**Backend Setup**
- [ ] Set up monorepo structure
  - [ ] Configure Python packages with Poetry
  - [ ] Set up TypeScript with pnpm workspaces
  - [ ] Configure Turborepo for build caching
- [ ] Development environment
  - [ ] Docker Compose for local development
  - [ ] PostgreSQL 15 database
  - [ ] Redis for caching
  - [ ] MinIO for S3-compatible storage
- [ ] CI/CD pipeline
  - [ ] GitHub Actions for tests
  - [ ] Automated linting (ruff, eslint)
  - [ ] Type checking (mypy, typescript)
  - [ ] Code coverage reporting

**Frontend Setup**
- [ ] Next.js 14 app with App Router
- [ ] Tailwind CSS + shadcn/ui components
- [ ] TypeScript strict mode
- [ ] React Query for data fetching
- [ ] Zustand for state management

**DevOps Setup**
- [ ] AWS infrastructure with Terraform
  - [ ] ECS Fargate for containers
  - [ ] RDS PostgreSQL
  - [ ] ElastiCache Redis
  - [ ] S3 for storage
- [ ] Monitoring and logging
  - [ ] DataDog or New Relic
  - [ ] Sentry for error tracking
  - [ ] CloudWatch logs

**Deliverables:**
- ✅ Working local development environment
- ✅ CI/CD pipeline running
- ✅ Staging environment deployed on AWS

---

### Sprint 2 (Weeks 3-4): Database Schema & Migrations

**Core Tables**
```sql
-- Users & Auth
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255),
  name VARCHAR(255),
  avatar_url TEXT,
  plan VARCHAR(50) DEFAULT 'free',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  token VARCHAR(255) UNIQUE NOT NULL,
  expires_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Billing & Subscriptions
CREATE TABLE subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  plan VARCHAR(50) NOT NULL,
  status VARCHAR(50) DEFAULT 'active',
  stripe_subscription_id VARCHAR(255),
  current_period_start TIMESTAMP,
  current_period_end TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE usage_records (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  resource_type VARCHAR(100) NOT NULL, -- 'scrape', 'api_call', 'pipeline_run'
  resource_id UUID,
  count INTEGER DEFAULT 1,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Scrapers
CREATE TABLE scrapers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  code TEXT NOT NULL,
  language VARCHAR(50) DEFAULT 'python',
  status VARCHAR(50) DEFAULT 'draft',
  is_public BOOLEAN DEFAULT FALSE,
  tags TEXT[],
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE scraper_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  scraper_id UUID REFERENCES scrapers(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  status VARCHAR(50) DEFAULT 'pending',
  input_data JSONB,
  output_data JSONB,
  error_message TEXT,
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  duration_ms INTEGER,
  created_at TIMESTAMP DEFAULT NOW()
);

-- AI Copilot
CREATE TABLE ai_conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  scraper_id UUID REFERENCES scrapers(id) ON DELETE SET NULL,
  messages JSONB NOT NULL,
  model VARCHAR(100),
  tokens_used INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- No-Code Workflows
CREATE TABLE workflows (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  workflow_json JSONB NOT NULL,
  status VARCHAR(50) DEFAULT 'draft',
  is_public BOOLEAN DEFAULT FALSE,
  template_id UUID REFERENCES workflow_templates(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE workflow_templates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  description TEXT,
  category VARCHAR(100),
  workflow_json JSONB NOT NULL,
  preview_image_url TEXT,
  is_premium BOOLEAN DEFAULT FALSE,
  price_cents INTEGER DEFAULT 0,
  downloads INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE workflow_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_id UUID REFERENCES workflows(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  status VARCHAR(50) DEFAULT 'pending',
  input_data JSONB,
  output_data JSONB,
  error_message TEXT,
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW()
);

-- API Marketplace
CREATE TABLE api_endpoints (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  creator_id UUID REFERENCES users(id) ON DELETE CASCADE,
  scraper_id UUID REFERENCES scrapers(id) ON DELETE CASCADE,
  endpoint_path VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  category VARCHAR(100),
  is_public BOOLEAN DEFAULT FALSE,
  price_tier VARCHAR(50) DEFAULT 'free',
  rate_limit_per_hour INTEGER DEFAULT 100,
  cache_ttl_seconds INTEGER DEFAULT 3600,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE api_keys (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  key_hash VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255),
  last_used_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  revoked_at TIMESTAMP
);

CREATE TABLE api_usage (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  api_key_id UUID REFERENCES api_keys(id) ON DELETE CASCADE,
  endpoint_id UUID REFERENCES api_endpoints(id) ON DELETE SET NULL,
  status_code INTEGER,
  response_time_ms INTEGER,
  cache_hit BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Data Pipelines
CREATE TABLE pipelines (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  dag_definition JSONB NOT NULL,
  schedule_cron VARCHAR(100),
  status VARCHAR(50) DEFAULT 'active',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE pipeline_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  pipeline_id UUID REFERENCES pipelines(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  status VARCHAR(50) DEFAULT 'pending',
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  metrics JSONB,
  error_message TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_scrapers_user_id ON scrapers(user_id);
CREATE INDEX idx_scraper_runs_scraper_id ON scraper_runs(scraper_id);
CREATE INDEX idx_scraper_runs_status ON scraper_runs(status);
CREATE INDEX idx_workflows_user_id ON workflows(user_id);
CREATE INDEX idx_api_usage_created_at ON api_usage(created_at);
CREATE INDEX idx_usage_records_user_id_created_at ON usage_records(user_id, created_at);
```

**Tasks:**
- [ ] Create SQLAlchemy models
- [ ] Set up Alembic migrations
- [ ] Create seed data script
- [ ] Write database tests

**Deliverables:**
- ✅ Complete database schema
- ✅ Migration scripts
- ✅ Database documentation

---

### Sprint 3 (Weeks 5-6): Authentication & User Management

**Backend API**
- [ ] User registration endpoint
  - [ ] Email validation
  - [ ] Password hashing (bcrypt)
  - [ ] Email verification flow
- [ ] Login endpoint
  - [ ] JWT token generation
  - [ ] Refresh token logic
  - [ ] Rate limiting (10 attempts per hour)
- [ ] OAuth integration
  - [ ] Google OAuth
  - [ ] GitHub OAuth
- [ ] User profile management
  - [ ] Update profile
  - [ ] Change password
  - [ ] Upload avatar (S3)
- [ ] Password reset flow
  - [ ] Reset token generation
  - [ ] Email sending (SendGrid)

**Frontend Pages**
- [ ] Sign up page
- [ ] Login page
- [ ] Email verification page
- [ ] Password reset page
- [ ] User profile page
- [ ] Settings page

**Security**
- [ ] CSRF protection
- [ ] Rate limiting middleware
- [ ] Input validation (Pydantic)
- [ ] SQL injection prevention
- [ ] XSS prevention

**Tasks:**
```python
# botasaurus_platform/auth/router.py
from fastapi import APIRouter, Depends, HTTPException, status
from .schemas import UserCreate, UserLogin, Token
from .service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=Token)
async def register(user: UserCreate, service: AuthService = Depends()):
    """Register a new user"""
    return await service.register(user)

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, service: AuthService = Depends()):
    """Login and get access token"""
    return await service.login(credentials)

@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str, service: AuthService = Depends()):
    """Refresh access token"""
    return await service.refresh_token(refresh_token)

@router.post("/logout")
async def logout(token: str, service: AuthService = Depends()):
    """Logout and invalidate token"""
    return await service.logout(token)

@router.post("/forgot-password")
async def forgot_password(email: str, service: AuthService = Depends()):
    """Send password reset email"""
    return await service.forgot_password(email)

@router.post("/reset-password")
async def reset_password(token: str, new_password: str, service: AuthService = Depends()):
    """Reset password with token"""
    return await service.reset_password(token, new_password)
```

**Deliverables:**
- ✅ Working auth system
- ✅ OAuth integration
- ✅ Frontend auth pages
- ✅ Auth middleware

---

### Sprint 4 (Weeks 7-8): Billing & Subscription System

**Stripe Integration**
- [ ] Stripe account setup
- [ ] Product & price configuration
- [ ] Webhook handling
  - [ ] `customer.subscription.created`
  - [ ] `customer.subscription.updated`
  - [ ] `customer.subscription.deleted`
  - [ ] `invoice.payment_succeeded`
  - [ ] `invoice.payment_failed`
- [ ] Subscription management
  - [ ] Create subscription
  - [ ] Update subscription (upgrade/downgrade)
  - [ ] Cancel subscription
  - [ ] Resume subscription
- [ ] Usage-based billing
  - [ ] Track API calls
  - [ ] Track scraper runs
  - [ ] Track pipeline executions
  - [ ] Monthly usage reports

**Backend API**
```python
# botasaurus_platform/billing/router.py
from fastapi import APIRouter, Depends
from .schemas import CheckoutSession, SubscriptionUpdate
from .service import BillingService

router = APIRouter(prefix="/billing", tags=["billing"])

@router.post("/create-checkout-session")
async def create_checkout_session(
    plan: str,
    service: BillingService = Depends()
):
    """Create Stripe checkout session"""
    return await service.create_checkout_session(plan)

@router.post("/create-portal-session")
async def create_portal_session(
    user_id: str,
    service: BillingService = Depends()
):
    """Create Stripe customer portal session"""
    return await service.create_portal_session(user_id)

@router.post("/webhook")
async def stripe_webhook(
    payload: bytes,
    signature: str,
    service: BillingService = Depends()
):
    """Handle Stripe webhooks"""
    return await service.handle_webhook(payload, signature)

@router.get("/subscription")
async def get_subscription(
    user_id: str,
    service: BillingService = Depends()
):
    """Get user's current subscription"""
    return await service.get_subscription(user_id)

@router.get("/usage")
async def get_usage(
    user_id: str,
    period: str,
    service: BillingService = Depends()
):
    """Get usage statistics for billing period"""
    return await service.get_usage(user_id, period)
```

**Frontend Pages**
- [ ] Pricing page
- [ ] Checkout page (Stripe Checkout)
- [ ] Billing dashboard
- [ ] Usage dashboard
- [ ] Invoice history

**Usage Tracking System**
- [ ] Usage middleware
- [ ] Quota enforcement
- [ ] Overage warnings
- [ ] Usage analytics

**Deliverables:**
- ✅ Stripe integration complete
- ✅ Subscription management working
- ✅ Usage tracking system
- ✅ Billing dashboard

---

### Sprint 5 (Weeks 9-10): Core API Infrastructure

**FastAPI Backend**
```python
# botasaurus_platform/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from .auth.router import router as auth_router
from .billing.router import router as billing_router
from .scrapers.router import router as scrapers_router
from .ai.router import router as ai_router
from .workflows.router import router as workflows_router
from .marketplace.router import router as marketplace_router
from .pipelines.router import router as pipelines_router

app = FastAPI(
    title="Botasaurus Platform API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Routers
app.include_router(auth_router)
app.include_router(billing_router)
app.include_router(scrapers_router)
app.include_router(ai_router)
app.include_router(workflows_router)
app.include_router(marketplace_router)
app.include_router(pipelines_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

**API Features**
- [ ] Request validation (Pydantic)
- [ ] Response serialization
- [ ] Error handling middleware
- [ ] Logging middleware
- [ ] Rate limiting
- [ ] API versioning
- [ ] OpenAPI documentation
- [ ] WebSocket support

**Deliverables:**
- ✅ Core API structure
- ✅ All routers scaffolded
- ✅ Middleware configured
- ✅ API documentation

---

### Sprint 6 (Weeks 11-12): Frontend Dashboard Foundation

**Next.js App Structure**
```
apps/web/
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   ├── register/
│   │   └── reset-password/
│   ├── (dashboard)/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── scrapers/
│   │   ├── workflows/
│   │   ├── ai-copilot/
│   │   ├── marketplace/
│   │   ├── pipelines/
│   │   ├── billing/
│   │   └── settings/
│   └── layout.tsx
├── components/
│   ├── ui/           # shadcn/ui components
│   ├── layout/       # Layout components
│   ├── forms/        # Form components
│   └── shared/       # Shared components
├── lib/
│   ├── api.ts        # API client
│   ├── auth.ts       # Auth utilities
│   └── hooks/        # Custom hooks
└── public/
```

**Core Components**
- [ ] Layout components
  - [ ] Sidebar navigation
  - [ ] Top navbar
  - [ ] Breadcrumbs
  - [ ] Footer
- [ ] Dashboard page
  - [ ] Stats cards
  - [ ] Recent activity
  - [ ] Quick actions
  - [ ] Usage charts
- [ ] Navigation
  - [ ] Sidebar menu
  - [ ] User menu
  - [ ] Notifications dropdown
- [ ] Forms
  - [ ] Input components
  - [ ] Form validation
  - [ ] Error messages
  - [ ] Loading states

**UI Components (shadcn/ui)**
- [ ] Button
- [ ] Input
- [ ] Select
- [ ] Dialog
- [ ] Dropdown
- [ ] Toast
- [ ] Table
- [ ] Card
- [ ] Badge
- [ ] Tabs
- [ ] Accordion

**State Management**
```typescript
// lib/stores/auth-store.ts
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  refreshToken: () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      login: async (email, password) => {
        const response = await api.post('/auth/login', { email, password })
        set({ user: response.user, token: response.token, isAuthenticated: true })
      },
      logout: () => {
        set({ user: null, token: null, isAuthenticated: false })
      },
      refreshToken: async () => {
        const { token } = get()
        const response = await api.post('/auth/refresh', { token })
        set({ token: response.token })
      }
    }),
    { name: 'auth-storage' }
  )
)
```

**Deliverables:**
- ✅ Dashboard layout complete
- ✅ Navigation working
- ✅ Core UI components
- ✅ State management setup

---

## Phase 2: AI Copilot MVP (Weeks 13-20)

**Goal:** Launch working AI Copilot that generates scraper code from natural language

**Team:** +1 AI/ML engineer (5 engineers total)

### Sprint 7 (Weeks 13-14): LLM Integration

**OpenAI Integration**
```python
# botasaurus_ai/llm_integrations/openai.py
from typing import List, Dict, Any
import openai
from .base import BaseLLMClient

class OpenAIClient(BaseLLMClient):
    """OpenAI API client"""

    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model

    def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """Generate completion using OpenAI API"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return response.choices[0].message.content

    def complete_with_vision(
        self,
        messages: List[Dict[str, Any]],
        images: List[bytes],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """Generate completion with vision (GPT-4V)"""
        import base64

        # Convert images to base64
        image_urls = []
        for img_bytes in images:
            b64_image = base64.b64encode(img_bytes).decode('utf-8')
            image_urls.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{b64_image}"
                }
            })

        # Add images to last message
        if messages:
            messages[-1]["content"] = [
                {"type": "text", "text": messages[-1]["content"]},
                *image_urls
            ]

        response = self.client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return response.choices[0].message.content

    def stream_complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ):
        """Stream completion tokens"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )

        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
```

**Anthropic Integration**
```python
# botasaurus_ai/llm_integrations/anthropic.py
from typing import List, Dict, Any
import anthropic
from .base import BaseLLMClient

class AnthropicClient(BaseLLMClient):
    """Anthropic Claude API client"""

    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """Generate completion using Claude API"""
        response = self.client.messages.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return response.content[0].text

    def complete_with_vision(
        self,
        messages: List[Dict[str, Any]],
        images: List[bytes],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """Generate completion with vision"""
        import base64

        # Claude supports images in messages
        image_content = []
        for img_bytes in images:
            b64_image = base64.b64encode(img_bytes).decode('utf-8')
            image_content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": b64_image
                }
            })

        # Add images to messages
        if messages:
            messages[-1]["content"] = [
                {"type": "text", "text": messages[-1]["content"]},
                *image_content
            ]

        response = self.client.messages.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        return response.content[0].text

    def stream_complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ):
        """Stream completion tokens"""
        with self.client.messages.stream(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        ) as stream:
            for text in stream.text_stream:
                yield text
```

**Tasks:**
- [ ] Implement OpenAI client
- [ ] Implement Anthropic client
- [ ] Add API key management
- [ ] Create LLM provider selector
- [ ] Add token counting
- [ ] Implement cost tracking
- [ ] Add fallback logic (OpenAI → Anthropic → Local)
- [ ] Write integration tests

**Deliverables:**
- ✅ Working LLM integrations
- ✅ Token usage tracking
- ✅ Cost tracking system

---

### Sprint 8 (Weeks 15-16): Code Generation Engine

**Prompt Engineering**
```python
# botasaurus_ai/prompts.py

SYSTEM_PROMPT = """You are an expert at generating Botasaurus web scraping code.

Botasaurus is a Python framework with three main decorators:

1. @browser - For browser-based scraping (Selenium-like)
   - Use for JavaScript-heavy sites
   - Supports human-like interactions
   - Example:
   ```python
   from botasaurus import browser

   @browser
   def scrape_page(driver, data):
       driver.get(data['url'])
       title = driver.find_element('#title').text
       return {'title': title}
   ```

2. @request - For HTTP request-based scraping
   - Use for static sites, APIs
   - Faster than browser
   - Example:
   ```python
   from botasaurus import request

   @request
   def scrape_api(request, data):
       response = request.get(data['url'])
       return response.json()
   ```

3. @task - For parallel processing without web
   - Use for data transformation
   - Example:
   ```python
   from botasaurus import task

   @task
   def process_data(data):
       return data['value'] * 2
   ```

Generate clean, well-documented Python code using appropriate decorators.
Always include error handling and follow best practices.
"""

USER_PROMPT_TEMPLATE = """Generate a Botasaurus scraper for the following task:

**Task:** {task_description}

{page_analysis}

{additional_context}

Generate complete, working Python code that:
1. Uses the appropriate decorator (@browser, @request, or @task)
2. Includes proper error handling
3. Returns structured data (dict or list of dicts)
4. Has clear variable names and comments
5. Follows Botasaurus best practices

Return ONLY the Python code, no explanations.
"""

def build_code_generation_prompt(
    task: str,
    page_analysis: Optional[Dict] = None,
    context: Optional[Dict] = None
) -> List[Dict[str, str]]:
    """Build prompt for code generation"""

    page_info = ""
    if page_analysis:
        page_info = f"""
**Page Analysis:**
- Page Type: {page_analysis.get('page_type', 'unknown')}
- Main Content Areas: {', '.join(page_analysis.get('main_content', []))}
- Recommended Selectors: {page_analysis.get('recommended_selectors', [])}
"""

    additional = ""
    if context:
        additional = f"""
**Additional Context:**
{context}
"""

    user_prompt = USER_PROMPT_TEMPLATE.format(
        task_description=task,
        page_analysis=page_info,
        additional_context=additional
    )

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]
```

**Code Generator Implementation**
```python
# botasaurus_ai/code_generator.py
from typing import Dict, List, Any, Optional
import re

class CodeGenerator:
    """Generates scraper code using LLM"""

    def __init__(self, llm_client):
        self.llm_client = llm_client

    def generate(
        self,
        prompt: str,
        page_analysis: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate scraper code from prompt"""

        # Build generation prompt
        messages = build_code_generation_prompt(
            task=prompt,
            page_analysis=page_analysis,
            context=context
        )

        # Add conversation history if exists
        if conversation_history:
            messages = conversation_history + messages[-1:]

        # Generate code
        generated_text = self.llm_client.complete(
            messages=messages,
            temperature=0.3,  # Lower for more consistent code
            max_tokens=2000
        )

        # Extract code from response
        code = self._extract_code(generated_text)

        # Extract explanation
        explanation = self._generate_explanation(code, prompt)

        # Extract selectors used
        selectors = self._extract_selectors(code)

        # Check for warnings
        warnings = self._check_warnings(code)

        return {
            "code": code,
            "explanation": explanation,
            "selectors": selectors,
            "warnings": warnings
        }

    def refine(
        self,
        current_code: str,
        refinement_prompt: str,
        conversation_history: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Refine existing code based on feedback"""

        messages = conversation_history + [
            {
                "role": "user",
                "content": f"""Current code:
```python
{current_code}
```

Refinement request: {refinement_prompt}

Generate the updated code incorporating the requested changes.
Return ONLY the complete updated Python code.
"""
            }
        ]

        generated_text = self.llm_client.complete(
            messages=messages,
            temperature=0.3,
            max_tokens=2000
        )

        refined_code = self._extract_code(generated_text)

        # Identify what changed
        changes = self._identify_changes(current_code, refined_code)

        return {
            "code": refined_code,
            "explanation": f"Updated code based on: {refinement_prompt}",
            "changes": changes
        }

    def _extract_code(self, text: str) -> str:
        """Extract Python code from LLM response"""
        # Look for code blocks
        code_block_pattern = r'```python\n(.*?)\n```'
        matches = re.findall(code_block_pattern, text, re.DOTALL)

        if matches:
            return matches[0].strip()

        # If no code block, return entire text (assume it's all code)
        return text.strip()

    def _extract_selectors(self, code: str) -> List[str]:
        """Extract CSS/XPath selectors from code"""
        selectors = []

        # CSS selectors
        css_pattern = r'["\']([#.][\w\-]+(?:\s+[\w\-]+)*)["\']'
        selectors.extend(re.findall(css_pattern, code))

        # XPath selectors
        xpath_pattern = r'["\'](//.+?)["\']'
        selectors.extend(re.findall(xpath_pattern, code))

        return list(set(selectors))

    def _check_warnings(self, code: str) -> List[str]:
        """Check for potential issues in generated code"""
        warnings = []

        if 'sleep(' in code:
            warnings.append("Code uses sleep() - consider using wait_for_element() instead")

        if 'find_elements' in code and 'if' not in code:
            warnings.append("Using find_elements without checking if elements exist")

        if '@browser' in code and 'try' not in code:
            warnings.append("No error handling found - consider adding try/except")

        return warnings

    def _generate_explanation(self, code: str, original_prompt: str) -> str:
        """Generate plain English explanation of code"""
        messages = [
            {
                "role": "system",
                "content": "You explain Python code in simple terms."
            },
            {
                "role": "user",
                "content": f"""Explain what this code does in 2-3 sentences:

```python
{code}
```

Original request: {original_prompt}
"""
            }
        ]

        return self.llm_client.complete(
            messages=messages,
            temperature=0.5,
            max_tokens=200
        )

    def _identify_changes(self, old_code: str, new_code: str) -> List[str]:
        """Identify what changed between code versions"""
        import difflib

        diff = list(difflib.unified_diff(
            old_code.splitlines(),
            new_code.splitlines(),
            lineterm=''
        ))

        changes = []
        for line in diff:
            if line.startswith('+') and not line.startswith('+++'):
                changes.append(f"Added: {line[1:].strip()}")
            elif line.startswith('-') and not line.startswith('---'):
                changes.append(f"Removed: {line[1:].strip()}")

        return changes[:10]  # Limit to top 10 changes
```

**Tasks:**
- [ ] Implement code generator
- [ ] Create prompt templates
- [ ] Add code extraction logic
- [ ] Implement selector extraction
- [ ] Add warning detection
- [ ] Create explanation generator
- [ ] Write unit tests

**Deliverables:**
- ✅ Working code generator
- ✅ Prompt templates
- ✅ Code extraction working
- ✅ Tests passing

---

### Sprint 9 (Weeks 17-18): Page Analyzer & Validator

**Page Analyzer with Vision**
```python
# botasaurus_ai/page_analyzer.py
from typing import Optional, Dict, Any
import base64
from playwright.async_api import async_playwright

class PageAnalyzer:
    """Analyzes page structure for scraper generation"""

    def __init__(self, llm_client, use_vision: bool = True):
        self.llm_client = llm_client
        self.use_vision = use_vision

    async def analyze(
        self,
        url: Optional[str] = None,
        screenshot: Optional[bytes] = None,
        html: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze a web page"""

        if url:
            screenshot, html = await self._fetch_page(url)

        analysis = {}

        # HTML analysis (fast)
        if html:
            analysis.update(self._analyze_html(html))

        # Vision analysis (more accurate but slower/expensive)
        if self.use_vision and screenshot:
            vision_analysis = await self._analyze_with_vision(screenshot, html)
            analysis.update(vision_analysis)

        return analysis

    async def _fetch_page(self, url: str) -> tuple[bytes, str]:
        """Fetch page screenshot and HTML"""
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url)
            await page.wait_for_load_state('networkidle')

            # Take screenshot
            screenshot = await page.screenshot(full_page=True)

            # Get HTML
            html = await page.content()

            await browser.close()

            return screenshot, html

    def _analyze_html(self, html: str) -> Dict[str, Any]:
        """Analyze HTML structure"""
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, 'html.parser')

        # Classify page type
        page_type = self._classify_page_type(soup)

        # Find main content areas
        main_content = self._find_main_content(soup)

        # Suggest selectors
        selectors = self._suggest_selectors(soup)

        return {
            "page_type": page_type,
            "main_content": main_content,
            "recommended_selectors": selectors,
            "complexity": self._assess_complexity(soup)
        }

    async def _analyze_with_vision(
        self,
        screenshot: bytes,
        html: Optional[str]
    ) -> Dict[str, Any]:
        """Analyze page using vision model"""

        prompt = """Analyze this webpage screenshot.

Identify:
1. Main content areas (header, navigation, main content, sidebar, footer)
2. Interactive elements (forms, buttons, search bars)
3. Data patterns (lists, tables, cards, grids)
4. Page type (e-commerce product, search results, article, profile, etc.)
5. Recommended scraping approach (browser vs requests)

Return structured JSON."""

        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]

        response = self.llm_client.complete_with_vision(
            messages=messages,
            images=[screenshot],
            temperature=0.3,
            max_tokens=500
        )

        # Parse JSON response
        import json
        try:
            return json.loads(response)
        except:
            # If not valid JSON, return basic structure
            return {"vision_analysis": response}

    def _classify_page_type(self, soup) -> str:
        """Classify page type from HTML"""
        # E-commerce indicators
        if soup.find(class_=re.compile('product|item|cart|price')):
            return "e-commerce"

        # Search results
        if soup.find(class_=re.compile('search-result|results')):
            return "search-results"

        # Article/blog
        if soup.find('article') or soup.find(class_=re.compile('post|article')):
            return "article"

        # Profile page
        if soup.find(class_=re.compile('profile|user-info')):
            return "profile"

        # List/directory
        if len(soup.find_all(class_=re.compile('card|item|entry'))) > 5:
            return "listing"

        return "general"

    def _find_main_content(self, soup) -> List[str]:
        """Find main content areas"""
        areas = []

        # Look for common content containers
        for selector in ['main', 'article', '#content', '.content', '.main']:
            if soup.select(selector):
                areas.append(selector)

        return areas[:5]

    def _suggest_selectors(self, soup) -> List[Dict[str, str]]:
        """Suggest selectors for common data"""
        selectors = []

        # Titles
        for tag in ['h1', 'h2', '.title', '.heading']:
            if soup.select(tag):
                selectors.append({"type": "title", "selector": tag})

        # Prices
        for selector in ['.price', '[class*="price"]', '[data-price]']:
            if soup.select(selector):
                selectors.append({"type": "price", "selector": selector})

        # Images
        if soup.select('img[src]'):
            selectors.append({"type": "image", "selector": "img[src]"})

        return selectors[:10]

    def _assess_complexity(self, soup) -> str:
        """Assess page complexity"""
        # Count interactive elements
        interactive = len(soup.find_all(['button', 'input', 'select', 'textarea']))

        # Count scripts
        scripts = len(soup.find_all('script'))

        if scripts > 20 or interactive > 10:
            return "high"
        elif scripts > 5 or interactive > 3:
            return "medium"
        return "low"
```

**Scraper Validator**
```python
# botasaurus_ai/scraper_validator.py
from typing import Dict, List, Any, Optional
import ast
import sys
from io import StringIO

class ScraperValidator:
    """Validates scraper code"""

    def validate(
        self,
        code: str,
        url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate scraper code"""

        errors = []
        warnings = []

        # Syntax check
        syntax_errors = self._check_syntax(code)
        errors.extend(syntax_errors)

        # Import check
        import_errors = self._check_imports(code)
        errors.extend(import_errors)

        # Decorator check
        decorator_warnings = self._check_decorators(code)
        warnings.extend(decorator_warnings)

        # Best practices check
        best_practice_warnings = self._check_best_practices(code)
        warnings.extend(best_practice_warnings)

        # Optional: Test execution
        if url and not errors:
            execution_result = self._test_execution(code, url)
            if not execution_result["success"]:
                errors.append(execution_result["error"])

        valid = len(errors) == 0
        fixable = self._is_fixable(errors)

        return {
            "valid": valid,
            "errors": errors,
            "warnings": warnings,
            "fixable": fixable
        }

    def _check_syntax(self, code: str) -> List[str]:
        """Check Python syntax"""
        try:
            ast.parse(code)
            return []
        except SyntaxError as e:
            return [f"Syntax error at line {e.lineno}: {e.msg}"]

    def _check_imports(self, code: str) -> List[str]:
        """Check required imports"""
        errors = []

        required_imports = {
            '@browser': 'from botasaurus import browser',
            '@request': 'from botasaurus import request',
            '@task': 'from botasaurus import task'
        }

        for decorator, import_line in required_imports.items():
            if decorator in code and import_line not in code:
                errors.append(f"Missing import for {decorator}: {import_line}")

        return errors

    def _check_decorators(self, code: str) -> List[str]:
        """Check decorator usage"""
        warnings = []

        # Check if function has decorator
        tree = ast.parse(code)
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

        for func in functions:
            if not func.decorator_list:
                warnings.append(f"Function '{func.name}' has no decorator")

            # Check parameters
            if '@browser' in code:
                if len(func.args.args) < 2:
                    warnings.append(f"@browser function should have (driver, data) parameters")

        return warnings

    def _check_best_practices(self, code: str) -> List[str]:
        """Check best practices"""
        warnings = []

        # Check for error handling
        if 'try' not in code and '@browser' in code:
            warnings.append("Consider adding try/except for error handling")

        # Check for returns
        tree = ast.parse(code)
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        for func in functions:
            has_return = any(isinstance(node, ast.Return) for node in ast.walk(func))
            if not has_return:
                warnings.append(f"Function '{func.name}' should return data")

        return warnings

    def _test_execution(self, code: str, url: str) -> Dict[str, Any]:
        """Test code execution (sandbox)"""
        try:
            # Create sandbox environment
            namespace = {}

            # Import botasaurus decorators
            exec("from botasaurus import browser, request, task", namespace)

            # Execute code
            exec(code, namespace)

            # Find decorated function
            func = None
            for name, obj in namespace.items():
                if callable(obj) and hasattr(obj, '__wrapped__'):
                    func = obj
                    break

            if not func:
                return {"success": False, "error": "No decorated function found"}

            # Test with sample data
            result = func({'url': url})

            return {"success": True, "result": result}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _is_fixable(self, errors: List[str]) -> bool:
        """Check if errors are auto-fixable"""
        fixable_keywords = ['Missing import', 'Indentation', 'expected']
        return any(any(keyword in error for keyword in fixable_keywords) for error in errors)
```

**Tasks:**
- [ ] Implement HTML analyzer
- [ ] Add vision-based analysis
- [ ] Create page classifier
- [ ] Implement syntax validator
- [ ] Add decorator validator
- [ ] Create test execution sandbox
- [ ] Write comprehensive tests

**Deliverables:**
- ✅ Page analyzer working
- ✅ Validator catching errors
- ✅ Vision analysis integrated
- ✅ Tests passing

---

### Sprint 10 (Weeks 19-20): AI Copilot Frontend & API

**Backend API**
```python
# botasaurus_platform/ai/router.py
from fastapi import APIRouter, Depends, HTTPException, WebSocket
from .schemas import GenerateRequest, RefineRequest, AnalyzePageRequest
from .service import AICopilotService

router = APIRouter(prefix="/ai", tags=["ai-copilot"])

@router.post("/generate")
async def generate_scraper(
    request: GenerateRequest,
    service: AICopilotService = Depends()
):
    """Generate scraper from natural language"""
    return await service.generate_scraper(
        user_id=request.user_id,
        prompt=request.prompt,
        url=request.url,
        context=request.context
    )

@router.post("/refine")
async def refine_scraper(
    request: RefineRequest,
    service: AICopilotService = Depends()
):
    """Refine existing scraper"""
    return await service.refine_scraper(
        conversation_id=request.conversation_id,
        refinement_prompt=request.refinement_prompt
    )

@router.post("/analyze-page")
async def analyze_page(
    request: AnalyzePageRequest,
    service: AICopilotService = Depends()
):
    """Analyze web page structure"""
    return await service.analyze_page(
        url=request.url,
        use_vision=request.use_vision
    )

@router.websocket("/ws/generate")
async def websocket_generate(
    websocket: WebSocket,
    service: AICopilotService = Depends()
):
    """WebSocket for streaming code generation"""
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_json()

            # Stream generated code
            async for chunk in service.stream_generate(
                prompt=data['prompt'],
                url=data.get('url')
            ):
                await websocket.send_json({"type": "chunk", "content": chunk})

            await websocket.send_json({"type": "complete"})

    except Exception as e:
        await websocket.send_json({"type": "error", "message": str(e)})
    finally:
        await websocket.close()

@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    service: AICopilotService = Depends()
):
    """Get AI conversation history"""
    return await service.get_conversation(conversation_id)

@router.get("/conversations")
async def list_conversations(
    user_id: str,
    service: AICopilotService = Depends()
):
    """List user's AI conversations"""
    return await service.list_conversations(user_id)
```

**Frontend - AI Copilot Page**
```typescript
// app/(dashboard)/ai-copilot/page.tsx
'use client'

import { useState } from 'react'
import { useAICopilot } from '@/lib/hooks/use-ai-copilot'
import { ChatInterface } from '@/components/ai/chat-interface'
import { CodePreview } from '@/components/ai/code-preview'
import { PageAnalyzer } from '@/components/ai/page-analyzer'

export default function AICopilotPage() {
  const [prompt, setPrompt] = useState('')
  const [url, setUrl] = useState('')
  const { generate, refine, generatedCode, loading, conversation } = useAICopilot()

  const handleGenerate = async () => {
    await generate({ prompt, url })
  }

  const handleRefine = async (refinement: string) => {
    await refine({ refinement })
  }

  return (
    <div className="flex h-screen">
      {/* Left Panel - Chat */}
      <div className="w-1/2 border-r">
        <div className="p-4 border-b">
          <h1 className="text-2xl font-bold">AI Scraping Copilot</h1>
          <p className="text-gray-600">Describe what you want to scrape</p>
        </div>

        <ChatInterface
          conversation={conversation}
          onSendMessage={handleGenerate}
          loading={loading}
        />

        {/* Input Area */}
        <div className="p-4 border-t">
          <input
            type="url"
            placeholder="URL to scrape (optional)"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="w-full mb-2 p-2 border rounded"
          />
          <textarea
            placeholder="Describe what you want to scrape..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="w-full p-2 border rounded"
            rows={4}
          />
          <div className="flex gap-2 mt-2">
            <button
              onClick={handleGenerate}
              disabled={loading || !prompt}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Generating...' : 'Generate Scraper'}
            </button>
            {url && (
              <button
                onClick={() => analyzePageAsync(url)}
                className="px-4 py-2 border rounded hover:bg-gray-50"
              >
                Analyze Page
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Right Panel - Code Preview */}
      <div className="w-1/2">
        <CodePreview
          code={generatedCode}
          onRefine={handleRefine}
          onSave={() => saveScraperAsync(generatedCode)}
          onTest={() => testScraperAsync(generatedCode, url)}
        />
      </div>
    </div>
  )
}
```

**Chat Interface Component**
```typescript
// components/ai/chat-interface.tsx
'use client'

import { Message } from '@/lib/types'
import { Avatar } from '@/components/ui/avatar'
import { ScrollArea } from '@/components/ui/scroll-area'

interface ChatInterfaceProps {
  conversation: Message[]
  onSendMessage: (message: string) => void
  loading: boolean
}

export function ChatInterface({ conversation, onSendMessage, loading }: ChatInterfaceProps) {
  return (
    <ScrollArea className="h-[calc(100vh-300px)]">
      <div className="p-4 space-y-4">
        {conversation.map((message, i) => (
          <div
            key={i}
            className={`flex gap-3 ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            {message.role === 'assistant' && (
              <Avatar>
                <span>🤖</span>
              </Avatar>
            )}
            <div
              className={`max-w-[80%] rounded-lg p-3 ${
                message.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-900'
              }`}
            >
              {message.content}
            </div>
            {message.role === 'user' && (
              <Avatar>
                <span>👤</span>
              </Avatar>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex gap-3">
            <Avatar>
              <span>🤖</span>
            </Avatar>
            <div className="bg-gray-100 rounded-lg p-3">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
              </div>
            </div>
          </div>
        )}
      </div>
    </ScrollArea>
  )
}
```

**Code Preview Component**
```typescript
// components/ai/code-preview.tsx
'use client'

import { useState } from 'react'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

interface CodePreviewProps {
  code: string
  onRefine: (refinement: string) => void
  onSave: () => void
  onTest: () => void
}

export function CodePreview({ code, onRefine, onSave, onTest }: CodePreviewProps) {
  const [refinement, setRefinement] = useState('')
  const [testResults, setTestResults] = useState<any>(null)

  return (
    <div className="flex flex-col h-full">
      <div className="p-4 border-b flex justify-between items-center">
        <h2 className="text-xl font-semibold">Generated Code</h2>
        <div className="flex gap-2">
          <Button onClick={onTest} variant="outline">
            Test Run
          </Button>
          <Button onClick={onSave}>Save Scraper</Button>
        </div>
      </div>

      <Tabs defaultValue="code" className="flex-1">
        <TabsList className="px-4">
          <TabsTrigger value="code">Code</TabsTrigger>
          <TabsTrigger value="explanation">Explanation</TabsTrigger>
          <TabsTrigger value="test">Test Results</TabsTrigger>
        </TabsList>

        <TabsContent value="code" className="flex-1 overflow-auto">
          {code ? (
            <SyntaxHighlighter
              language="python"
              style={vscDarkPlus}
              customStyle={{ margin: 0, height: '100%' }}
            >
              {code}
            </SyntaxHighlighter>
          ) : (
            <div className="flex items-center justify-center h-full text-gray-400">
              Generated code will appear here
            </div>
          )}
        </TabsContent>

        <TabsContent value="explanation" className="p-4">
          <div className="prose">
            <h3>How it works</h3>
            <p>Explanation of generated code...</p>
          </div>
        </TabsContent>

        <TabsContent value="test" className="p-4">
          {testResults ? (
            <div>
              <h3 className="font-semibold mb-2">Test Results</h3>
              <pre className="bg-gray-100 p-4 rounded">
                {JSON.stringify(testResults, null, 2)}
              </pre>
            </div>
          ) : (
            <div className="text-gray-400">Run a test to see results</div>
          )}
        </TabsContent>
      </Tabs>

      {/* Refinement Input */}
      {code && (
        <div className="p-4 border-t">
          <textarea
            placeholder="Request changes or refinements..."
            value={refinement}
            onChange={(e) => setRefinement(e.target.value)}
            className="w-full p-2 border rounded"
            rows={2}
          />
          <Button
            onClick={() => {
              onRefine(refinement)
              setRefinement('')
            }}
            disabled={!refinement}
            className="mt-2"
          >
            Refine Code
          </Button>
        </div>
      )}
    </div>
  )
}
```

**Tasks:**
- [ ] Implement AI backend API
- [ ] Create WebSocket streaming
- [ ] Build chat interface
- [ ] Create code preview component
- [ ] Add page analyzer UI
- [ ] Implement test runner
- [ ] Add save scraper functionality
- [ ] Write E2E tests

**Deliverables:**
- ✅ AI Copilot API complete
- ✅ Frontend working
- ✅ Streaming code generation
- ✅ Save & test functionality

---

## Phase 3: No-Code Builder (Weeks 21-32)

**Goal:** Launch visual drag-drop scraper builder

### Sprint 11 (Weeks 21-22): Workflow Engine Backend

[Continue with detailed implementation plans for remaining phases...]

---

## Development Standards

### Code Quality
- **Test Coverage:** Minimum 80%
- **Type Safety:** 100% typed (Python: mypy, TS: strict)
- **Linting:** Pass ruff (Python) and eslint (TS)
- **Documentation:** All public APIs documented

### Git Workflow
- **Branch Naming:** `feature/component-name`, `fix/issue-description`
- **Commits:** Conventional commits (feat:, fix:, docs:, etc.)
- **PRs:** Require 2 approvals, all tests passing
- **Merge:** Squash and merge

### Testing Strategy
- **Unit Tests:** 70% coverage minimum
- **Integration Tests:** Critical paths covered
- **E2E Tests:** Main user flows
- **Performance Tests:** API response times < 200ms

### Deployment
- **Environments:** dev → staging → production
- **Deploy Schedule:** Mon-Thu (no Friday deploys)
- **Rollback Plan:** One-click rollback available
- **Monitoring:** DataDog dashboards for all services

---

## Success Metrics

### Phase 1 (Foundation)
- ✅ All services running in staging
- ✅ CI/CD pipeline 100% reliable
- ✅ Database migrations tested
- ✅ Auth system secure (penetration tested)
- ✅ Billing integration working (test mode)

### Phase 2 (AI Copilot MVP)
- ✅ AI generates valid code 90% of time
- ✅ Average generation time < 10 seconds
- ✅ User satisfaction score > 4/5
- ✅ 100 beta users actively using
- ✅ 70% of generated scrapers work without modification

### Phase 3 (No-Code Builder)
- ✅ 50 workflow templates available
- ✅ Average workflow creation time < 10 minutes
- ✅ 85% workflow success rate
- ✅ 500 workflows created in first month
- ✅ 40% conversion from free to paid

### Phase 4 (API Marketplace)
- ✅ 20 APIs available
- ✅ 1,000 API calls per day
- ✅ Average API response time < 500ms
- ✅ 95% cache hit rate
- ✅ $1K+ MRR from API usage

### Phase 5 (Data Pipelines)
- ✅ 10 connectors available
- ✅ 100 pipelines created
- ✅ 99% pipeline success rate
- ✅ Average pipeline execution < 5 minutes
- ✅ 30% of Pro users using pipelines

### Phase 6 (Launch)
- ✅ 2,000 registered users
- ✅ 500 paying customers
- ✅ $30K MRR
- ✅ < 5% churn rate
- ✅ NPS score > 40

---

**Next Steps:**
1. Review this plan with team
2. Set up project management (Linear/Jira)
3. Begin Sprint 1 immediately
4. Weekly progress reviews
5. Bi-weekly demos to stakeholders

Let's build! 🚀
