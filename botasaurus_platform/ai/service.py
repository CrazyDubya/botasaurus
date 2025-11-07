"""
AI Copilot Service
===================

Service layer integrating all AI components for scraper generation.
"""

from typing import Dict, Any, Optional, List
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy.orm import Session

from botasaurus_ai import CodeGenerator, PageAnalyzer, ScraperValidator
from botasaurus_ai.llm_integrations import create_llm_client

from ..core.database.models import (
    AIConversation, AIConversationMessage, UsageRecord, User
)
from .schemas import (
    GeneratedCode, RefinedCode, PageAnalysis, ValidationResult,
    AutoFixResult, ConversationResponse, UsageStats
)


class AICopilotService:
    """Main service for AI-powered scraper generation"""

    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user

        # Initialize LLM client based on user preferences or default
        self.llm_client = self._get_llm_client()

        # Initialize AI components
        self.code_generator = CodeGenerator(self.llm_client)
        self.page_analyzer = PageAnalyzer(self.llm_client, use_vision=True)
        self.validator = ScraperValidator()

    def _get_llm_client(self):
        """Get LLM client based on configuration"""
        from ..core.config import settings

        # Try OpenAI first
        if settings.OPENAI_API_KEY:
            return create_llm_client("openai", api_key=settings.OPENAI_API_KEY)

        # Fallback to Anthropic
        elif settings.ANTHROPIC_API_KEY:
            return create_llm_client("anthropic", api_key=settings.ANTHROPIC_API_KEY)

        else:
            raise ValueError("No LLM API key configured. Set OPENAI_API_KEY or ANTHROPIC_API_KEY")

    async def generate_scraper(
        self,
        prompt: str,
        url: Optional[str] = None,
        use_vision: bool = True,
        context: Optional[Dict[str, Any]] = None,
        conversation_id: Optional[UUID] = None
    ) -> GeneratedCode:
        """
        Generate scraper from natural language prompt.

        This is the main entry point for AI scraper generation.
        """

        # Get or create conversation
        if conversation_id:
            conversation = self._get_conversation(conversation_id)
        else:
            conversation = self._create_conversation(f"Generate: {prompt[:50]}")
            conversation_id = conversation.id

        # Add user message to conversation
        self._add_message(conversation_id, "user", prompt)

        # Analyze page if URL provided
        page_analysis = None
        if url:
            try:
                page_analysis = await self.page_analyzer.analyze(
                    url=url,
                    use_vision=use_vision
                )
            except Exception as e:
                # Continue without page analysis if it fails
                page_analysis = {"error": str(e)}

        # Get conversation history for context
        history = self._get_conversation_history(conversation_id)

        # Generate code
        result = self.code_generator.generate(
            prompt=prompt,
            page_analysis=page_analysis,
            conversation_history=history,
            context=context
        )

        # Validate generated code
        validation = self.validator.validate(result["code"])

        # If validation fails but fixable, try to auto-fix
        if not validation["valid"] and validation["fixable"]:
            try:
                result = await self._auto_fix(result["code"], validation, conversation_id)
            except:
                pass  # Keep original if auto-fix fails

        # Add assistant response to conversation
        self._add_message(
            conversation_id,
            "assistant",
            result["code"],
            metadata={
                "explanation": result["explanation"],
                "selectors": result["selectors"],
                "warnings": result["warnings"],
                "validation": validation
            }
        )

        # Track usage
        tokens_used = self._estimate_tokens(prompt, result["code"])
        self._track_usage(
            feature="generate_scraper",
            tokens_used=tokens_used,
            success=validation["valid"]
        )

        return GeneratedCode(
            code=result["code"],
            explanation=result["explanation"],
            selectors=result["selectors"],
            warnings=result["warnings"] + validation.get("warnings", []),
            conversation_id=conversation_id,
            tokens_used=tokens_used
        )

    async def refine_scraper(
        self,
        current_code: str,
        refinement_prompt: str,
        conversation_id: UUID
    ) -> RefinedCode:
        """Refine existing scraper based on user feedback"""

        conversation = self._get_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")

        # Add refinement request to conversation
        self._add_message(conversation_id, "user", refinement_prompt)

        # Get conversation history
        history = self._get_conversation_history(conversation_id)

        # Refine code
        result = self.code_generator.refine(
            current_code=current_code,
            refinement_prompt=refinement_prompt,
            conversation_history=history
        )

        # Validate refined code
        validation = self.validator.validate(result["code"])

        # Add assistant response
        self._add_message(
            conversation_id,
            "assistant",
            result["code"],
            metadata={
                "explanation": result["explanation"],
                "changes": result["changes"],
                "validation": validation
            }
        )

        # Track usage
        tokens_used = self._estimate_tokens(refinement_prompt, result["code"])
        self._track_usage(
            feature="refine_scraper",
            tokens_used=tokens_used,
            success=validation["valid"]
        )

        return RefinedCode(
            code=result["code"],
            explanation=result["explanation"],
            changes=result["changes"],
            conversation_id=conversation_id,
            tokens_used=tokens_used
        )

    async def analyze_page(
        self,
        url: Optional[str] = None,
        html: Optional[str] = None,
        screenshot: Optional[bytes] = None,
        use_vision: bool = True
    ) -> PageAnalysis:
        """Analyze page structure"""

        analysis = await self.page_analyzer.analyze(
            url=url,
            html=html,
            screenshot=screenshot
        )

        # Track usage (page analysis uses tokens for vision)
        if use_vision:
            self._track_usage(
                feature="analyze_page",
                tokens_used=500,  # Estimate for vision analysis
                success=True
            )

        return PageAnalysis(**analysis)

    def validate_code(
        self,
        code: str,
        url: Optional[str] = None,
        test_execution: bool = False
    ) -> ValidationResult:
        """Validate scraper code"""

        result = self.validator.validate(
            code=code,
            url=url,
            test_execution=test_execution
        )

        return ValidationResult(**result)

    async def _auto_fix(
        self,
        code: str,
        validation_result: Dict[str, Any],
        conversation_id: UUID
    ) -> Dict[str, Any]:
        """Attempt to automatically fix validation errors"""

        # Build fix prompt
        errors_text = "\n".join(f"- {error}" for error in validation_result["errors"])
        fix_prompt = f"""Fix the following errors in this code:

{errors_text}

Original code:
```python
{code}
```

Return only the fixed code."""

        # Use refinement to fix
        history = self._get_conversation_history(conversation_id)
        result = self.code_generator.refine(
            current_code=code,
            refinement_prompt=fix_prompt,
            conversation_history=history
        )

        return result

    # ==================== Conversation Management ====================

    def _create_conversation(self, title: str) -> AIConversation:
        """Create new conversation"""
        conversation = AIConversation(
            id=uuid4(),
            user_id=self.user.id,
            title=title,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        return conversation

    def _get_conversation(self, conversation_id: UUID) -> Optional[AIConversation]:
        """Get conversation by ID"""
        return self.db.query(AIConversation).filter(
            AIConversation.id == conversation_id,
            AIConversation.user_id == self.user.id
        ).first()

    def _add_message(
        self,
        conversation_id: UUID,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add message to conversation"""
        message = AIConversationMessage(
            id=uuid4(),
            conversation_id=conversation_id,
            role=role,
            content=content,
            metadata=metadata,
            created_at=datetime.utcnow()
        )
        self.db.add(message)

        # Update conversation timestamp
        conversation = self._get_conversation(conversation_id)
        if conversation:
            conversation.updated_at = datetime.utcnow()

        self.db.commit()

    def _get_conversation_history(self, conversation_id: UUID) -> List[Dict[str, str]]:
        """Get conversation history formatted for LLM"""
        messages = self.db.query(AIConversationMessage).filter(
            AIConversationMessage.conversation_id == conversation_id
        ).order_by(AIConversationMessage.created_at).all()

        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

    def get_conversations(self, limit: int = 50) -> List[ConversationResponse]:
        """Get user's conversations"""
        conversations = self.db.query(AIConversation).filter(
            AIConversation.user_id == self.user.id
        ).order_by(AIConversation.updated_at.desc()).limit(limit).all()

        return [ConversationResponse.model_validate(conv) for conv in conversations]

    # ==================== Usage Tracking ====================

    def _track_usage(
        self,
        feature: str,
        tokens_used: int,
        success: bool,
        cost: Optional[float] = None
    ):
        """Track AI usage"""

        if cost is None:
            # Estimate cost (rough approximations)
            # GPT-4: $0.03 per 1K input tokens, $0.06 per 1K output tokens
            # Average: $0.045 per 1K tokens
            cost = (tokens_used / 1000) * 0.045

        record = UsageRecord(
            id=uuid4(),
            user_id=self.user.id,
            feature=feature,
            tokens_used=tokens_used,
            cost=cost,
            model=getattr(self.llm_client, 'model', 'unknown'),
            success=success,
            created_at=datetime.utcnow()
        )
        self.db.add(record)
        self.db.commit()

    def get_usage_stats(self) -> UsageStats:
        """Get usage statistics for user"""
        records = self.db.query(UsageRecord).filter(
            UsageRecord.user_id == self.user.id
        ).all()

        total_tokens = sum(r.tokens_used for r in records)
        total_cost = sum(r.cost for r in records)
        requests_count = len(records)
        successful = sum(1 for r in records if r.success)
        failed = requests_count - successful

        return UsageStats(
            total_tokens=total_tokens,
            total_cost=total_cost,
            requests_count=requests_count,
            successful_generations=successful,
            failed_generations=failed
        )

    # ==================== Helpers ====================

    def _estimate_tokens(self, prompt: str, code: str) -> int:
        """Rough token estimation (1 token ≈ 4 chars)"""
        total_chars = len(prompt) + len(code)
        return total_chars // 4
