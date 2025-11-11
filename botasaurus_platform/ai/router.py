"""
AI Copilot API Router
======================

FastAPI routes for AI-powered scraper generation.
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import json
import asyncio

from ..core.database import get_db
from ..core.database.models import User
from ..auth.dependencies import get_current_user

from .service import AICopilotService
from .schemas import (
    GenerateScraperRequest, GeneratedCode,
    RefineScraperRequest, RefinedCode,
    AnalyzePageRequest, PageAnalysis,
    ValidateCodeRequest, ValidationResult,
    ConversationResponse, UsageStats,
    StreamChunk, StreamComplete,
    CreateConversationRequest
)


router = APIRouter(prefix="/ai", tags=["ai-copilot"])


# ==================== REST Endpoints ====================

@router.post("/generate", response_model=GeneratedCode)
async def generate_scraper(
    request: GenerateScraperRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Generate a new scraper from natural language prompt.

    This is the main AI Copilot endpoint. Provide a description of what
    you want to scrape, optionally with a URL, and get back working code.

    Example:
        POST /api/ai/generate
        {
            "prompt": "Scrape product names and prices from Amazon",
            "url": "https://www.amazon.com/s?k=laptops",
            "use_vision": true
        }
    """
    service = AICopilotService(db, user)

    try:
        result = await service.generate_scraper(
            prompt=request.prompt,
            url=request.url,
            use_vision=request.use_vision,
            context=request.context,
            conversation_id=request.conversation_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.post("/refine", response_model=RefinedCode)
async def refine_scraper(
    request: RefineScraperRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Refine existing scraper code based on feedback.

    Use this to iteratively improve generated code. Requires a conversation_id
    from a previous generation.

    Example:
        POST /api/ai/refine
        {
            "current_code": "from botasaurus import browser...",
            "refinement_prompt": "Add error handling and retry logic",
            "conversation_id": "uuid-here"
        }
    """
    service = AICopilotService(db, user)

    try:
        result = await service.refine_scraper(
            current_code=request.current_code,
            refinement_prompt=request.refinement_prompt,
            conversation_id=request.conversation_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refinement failed: {str(e)}")


@router.post("/analyze-page", response_model=PageAnalysis)
async def analyze_page(
    request: AnalyzePageRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Analyze page structure using vision and HTML parsing.

    Provides insights about page type, complexity, and recommended selectors
    before generating code.

    Example:
        POST /api/ai/analyze-page
        {
            "url": "https://example.com/products",
            "use_vision": true
        }
    """
    service = AICopilotService(db, user)

    try:
        result = await service.analyze_page(
            url=request.url,
            html=request.html,
            screenshot=request.screenshot,
            use_vision=request.use_vision
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/validate", response_model=ValidationResult)
def validate_code(
    request: ValidateCodeRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Validate scraper code for syntax, security, and best practices.

    Returns detailed validation results with errors, warnings, and whether
    issues are auto-fixable.

    Example:
        POST /api/ai/validate
        {
            "code": "from botasaurus import browser\\n\\n@browser\\ndef scrape(driver, data):\\n    ...",
            "url": "https://example.com"
        }
    """
    service = AICopilotService(db, user)

    try:
        result = service.validate_code(
            code=request.code,
            url=request.url,
            test_execution=request.test_execution
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


# ==================== Conversation Management ====================

@router.post("/conversations", response_model=ConversationResponse)
def create_conversation(
    request: CreateConversationRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Create a new AI conversation.

    Conversations maintain context across multiple generation/refinement requests.
    """
    service = AICopilotService(db, user)
    conversation = service._create_conversation(request.title)

    if request.initial_prompt:
        service._add_message(conversation.id, "user", request.initial_prompt)

    return ConversationResponse.model_validate(conversation)


@router.get("/conversations", response_model=List[ConversationResponse])
def get_conversations(
    limit: int = 50,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get user's AI conversations"""
    service = AICopilotService(db, user)
    return service.get_conversations(limit=limit)


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get specific conversation with full message history"""
    service = AICopilotService(db, user)
    conversation = service._get_conversation(conversation_id)

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return ConversationResponse.model_validate(conversation)


# ==================== Usage Stats ====================

@router.get("/usage", response_model=UsageStats)
def get_usage_stats(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Get AI usage statistics for current user.

    Returns token usage, costs, and request counts.
    """
    service = AICopilotService(db, user)
    return service.get_usage_stats()


# ==================== WebSocket Streaming ====================

@router.websocket("/ws/generate")
async def websocket_generate(
    websocket: WebSocket,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for streaming code generation.

    Provides real-time code generation with progressive updates.

    Protocol:
        Client sends:
        {
            "action": "generate",
            "token": "jwt-token",
            "prompt": "Scrape product data",
            "url": "https://example.com",
            "use_vision": true
        }

        Server sends (multiple chunks):
        {
            "type": "code",
            "content": "from botasaurus import browser\n\n"
        }
        {
            "type": "code",
            "content": "@browser\ndef scrape(driver, data):\n"
        }
        ...
        {
            "type": "complete",
            "conversation_id": "uuid",
            "tokens_used": 1500,
            "warnings": [],
            "selectors": [".product-title"]
        }
    """
    await websocket.accept()

    try:
        # Receive initial request
        data = await websocket.receive_json()

        # Authenticate user from token
        token = data.get("token")
        if not token:
            await websocket.send_json({
                "type": "error",
                "content": "Authentication token required"
            })
            await websocket.close()
            return

        # TODO: Verify JWT token and get user
        # For now, mock user validation
        try:
            from ..auth.service import AuthService
            auth_service = AuthService(db)
            payload = auth_service.verify_token(token)
            from uuid import UUID
            user_id = UUID(payload.get("sub"))
            user = auth_service.get_user_by_id(user_id)

            if not user:
                raise ValueError("Invalid user")
        except Exception as e:
            await websocket.send_json({
                "type": "error",
                "content": f"Authentication failed: {str(e)}"
            })
            await websocket.close()
            return

        # Initialize service
        service = AICopilotService(db, user)

        # Extract request data
        action = data.get("action", "generate")
        prompt = data.get("prompt")
        url = data.get("url")
        use_vision = data.get("use_vision", True)
        conversation_id = data.get("conversation_id")

        if action == "generate":
            # Send initial message
            await websocket.send_json({
                "type": "status",
                "content": "Analyzing page and generating code..."
            })

            # Analyze page if URL provided (with progress updates)
            page_analysis = None
            if url:
                await websocket.send_json({
                    "type": "status",
                    "content": "Analyzing page structure..."
                })
                try:
                    page_analysis = await service.page_analyzer.analyze(
                        url=url,
                        use_vision=use_vision
                    )
                    await websocket.send_json({
                        "type": "analysis",
                        "content": json.dumps(page_analysis)
                    })
                except Exception as e:
                    await websocket.send_json({
                        "type": "warning",
                        "content": f"Page analysis failed: {str(e)}"
                    })

            # Stream code generation
            await websocket.send_json({
                "type": "status",
                "content": "Generating code..."
            })

            # Get conversation
            if conversation_id:
                conversation = service._get_conversation(UUID(conversation_id))
            else:
                conversation = service._create_conversation(f"Generate: {prompt[:50]}")
                conversation_id = str(conversation.id)

            service._add_message(UUID(conversation_id), "user", prompt)

            # Get history
            history = service._get_conversation_history(UUID(conversation_id))

            # Build messages for streaming
            from botasaurus_ai.prompts import build_code_generation_prompt
            messages = build_code_generation_prompt(
                task=prompt,
                page_analysis=page_analysis,
                context=None
            )

            # Stream generation
            full_code = ""
            try:
                for chunk in service.llm_client.stream_complete(
                    messages=messages,
                    temperature=0.3,
                    max_tokens=2000
                ):
                    full_code += chunk
                    await websocket.send_json({
                        "type": "code",
                        "content": chunk
                    })
                    # Small delay to not overwhelm client
                    await asyncio.sleep(0.01)

            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "content": f"Generation error: {str(e)}"
                })
                await websocket.close()
                return

            # Extract and validate code
            from botasaurus_ai.code_generator import CodeGenerator
            generator = CodeGenerator(service.llm_client)
            code = generator._extract_code(full_code)
            selectors = generator._extract_selectors(code)
            warnings = generator._check_warnings(code)

            # Validate
            validation = service.validator.validate(code)
            if not validation["valid"]:
                warnings.extend([f"Validation: {e}" for e in validation["errors"]])

            # Save to conversation
            service._add_message(
                UUID(conversation_id),
                "assistant",
                code,
                metadata={"selectors": selectors, "warnings": warnings}
            )

            # Track usage
            tokens_used = service._estimate_tokens(prompt, code)
            service._track_usage(
                feature="generate_scraper_ws",
                tokens_used=tokens_used,
                success=validation["valid"]
            )

            # Send completion
            await websocket.send_json({
                "type": "complete",
                "conversation_id": conversation_id,
                "tokens_used": tokens_used,
                "warnings": warnings,
                "selectors": selectors,
                "validation": validation
            })

        elif action == "refine":
            # Similar streaming for refinement
            current_code = data.get("current_code")
            refinement_prompt = data.get("refinement_prompt")

            await websocket.send_json({
                "type": "status",
                "content": "Refining code..."
            })

            # TODO: Implement streaming refinement
            # For now, fall back to non-streaming
            result = await service.refine_scraper(
                current_code=current_code,
                refinement_prompt=refinement_prompt,
                conversation_id=UUID(conversation_id)
            )

            await websocket.send_json({
                "type": "code",
                "content": result.code
            })

            await websocket.send_json({
                "type": "complete",
                "conversation_id": str(result.conversation_id),
                "tokens_used": result.tokens_used,
                "changes": result.changes
            })

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        try:
            await websocket.send_json({
                "type": "error",
                "content": str(e)
            })
        except:
            pass
        await websocket.close()
