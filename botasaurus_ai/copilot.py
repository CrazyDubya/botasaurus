"""
AI Scraping Copilot
===================

Main orchestration layer for AI-powered scraper generation.
"""

from typing import Dict, List, Optional, Any
import json


class ScraperCopilot:
    """
    AI-powered assistant for generating web scrapers from natural language.

    Features:
    - Converts user prompts to working scraper code
    - Analyzes web pages to understand structure
    - Generates appropriate Botasaurus decorators (@browser, @request, @task)
    - Validates and tests generated code
    - Provides interactive refinement

    Example:
        >>> copilot = ScraperCopilot(llm_provider="openai")
        >>> result = copilot.generate_scraper(
        ...     prompt="Scrape product titles and prices from Amazon",
        ...     url="https://www.amazon.com/s?k=laptops"
        ... )
        >>> print(result["code"])
    """

    def __init__(
        self,
        llm_provider: str = "openai",
        api_key: Optional[str] = None,
        model: str = "gpt-4",
        use_vision: bool = True
    ):
        """
        Initialize the AI Copilot.

        Args:
            llm_provider: LLM provider ("openai", "anthropic", "local")
            api_key: API key for the LLM provider
            model: Specific model to use (e.g., "gpt-4", "claude-3-opus")
            use_vision: Whether to use vision models for page analysis
        """
        self.llm_provider = llm_provider
        self.api_key = api_key
        self.model = model
        self.use_vision = use_vision

        self.conversation_history: List[Dict[str, str]] = []
        self.generated_code: Optional[str] = None

        # Lazy load LLM client
        self._llm_client = None
        self._page_analyzer = None
        self._code_generator = None
        self._selector_finder = None
        self._validator = None

    @property
    def llm_client(self):
        """Lazy load LLM client"""
        if self._llm_client is None:
            from .llm_integrations import get_llm_client
            self._llm_client = get_llm_client(
                provider=self.llm_provider,
                api_key=self.api_key,
                model=self.model
            )
        return self._llm_client

    @property
    def page_analyzer(self):
        """Lazy load page analyzer"""
        if self._page_analyzer is None:
            from .page_analyzer import PageAnalyzer
            self._page_analyzer = PageAnalyzer(
                llm_client=self.llm_client,
                use_vision=self.use_vision
            )
        return self._page_analyzer

    @property
    def code_generator(self):
        """Lazy load code generator"""
        if self._code_generator is None:
            from .code_generator import CodeGenerator
            self._code_generator = CodeGenerator(llm_client=self.llm_client)
        return self._code_generator

    @property
    def selector_finder(self):
        """Lazy load selector finder"""
        if self._selector_finder is None:
            from .selector_finder import SelectorFinder
            self._selector_finder = SelectorFinder(llm_client=self.llm_client)
        return self._selector_finder

    @property
    def validator(self):
        """Lazy load scraper validator"""
        if self._validator is None:
            from .scraper_validator import ScraperValidator
            self._validator = ScraperValidator()
        return self._validator

    def generate_scraper(
        self,
        prompt: str,
        url: Optional[str] = None,
        screenshot: Optional[bytes] = None,
        html: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a scraper from a natural language prompt.

        Args:
            prompt: User's natural language description of scraping task
            url: Optional URL to analyze
            screenshot: Optional screenshot bytes for vision analysis
            html: Optional HTML content for analysis
            context: Additional context (existing code, constraints, etc.)

        Returns:
            Dict containing:
                - code: Generated scraper code
                - explanation: Plain English explanation
                - selectors: Recommended CSS/XPath selectors
                - warnings: Any potential issues
                - test_results: Validation results
        """
        # Add prompt to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": prompt
        })

        # Step 1: Analyze the page if URL/screenshot/HTML provided
        page_analysis = None
        if url or screenshot or html:
            page_analysis = self.page_analyzer.analyze(
                url=url,
                screenshot=screenshot,
                html=html
            )

        # Step 2: Generate scraper code
        generation_result = self.code_generator.generate(
            prompt=prompt,
            page_analysis=page_analysis,
            conversation_history=self.conversation_history,
            context=context
        )

        self.generated_code = generation_result["code"]

        # Step 3: Validate generated code
        validation_result = self.validator.validate(
            code=self.generated_code,
            url=url
        )

        # Step 4: Auto-fix if validation fails
        if not validation_result["valid"] and validation_result["fixable"]:
            fix_result = self.auto_fix(
                code=self.generated_code,
                errors=validation_result["errors"]
            )
            if fix_result["success"]:
                self.generated_code = fix_result["fixed_code"]
                validation_result = self.validator.validate(
                    code=self.generated_code,
                    url=url
                )

        # Add response to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": generation_result["explanation"]
        })

        return {
            "code": self.generated_code,
            "explanation": generation_result["explanation"],
            "selectors": generation_result.get("selectors", []),
            "warnings": generation_result.get("warnings", []),
            "test_results": validation_result,
            "page_analysis": page_analysis
        }

    def refine_scraper(
        self,
        refinement_prompt: str,
        current_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Refine existing scraper based on user feedback.

        Args:
            refinement_prompt: User's refinement request
            current_code: Current scraper code (uses last generated if None)

        Returns:
            Dict with updated code and explanation
        """
        code_to_refine = current_code or self.generated_code

        if not code_to_refine:
            raise ValueError("No code to refine. Generate a scraper first.")

        # Add refinement to conversation
        self.conversation_history.append({
            "role": "user",
            "content": refinement_prompt
        })

        # Generate refined code
        refinement_result = self.code_generator.refine(
            current_code=code_to_refine,
            refinement_prompt=refinement_prompt,
            conversation_history=self.conversation_history
        )

        self.generated_code = refinement_result["code"]

        # Validate refined code
        validation_result = self.validator.validate(code=self.generated_code)

        self.conversation_history.append({
            "role": "assistant",
            "content": refinement_result["explanation"]
        })

        return {
            "code": self.generated_code,
            "explanation": refinement_result["explanation"],
            "changes": refinement_result.get("changes", []),
            "test_results": validation_result
        }

    def auto_fix(
        self,
        code: str,
        errors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Automatically fix errors in generated scraper.

        Args:
            code: Scraper code with errors
            errors: List of error details from validation

        Returns:
            Dict with fixed code and success status
        """
        from .auto_fixer import AutoFixer

        fixer = AutoFixer(llm_client=self.llm_client)
        return fixer.fix(code=code, errors=errors)

    def find_selectors(
        self,
        description: str,
        html: Optional[str] = None,
        url: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Find CSS/XPath selectors for described elements.

        Args:
            description: Natural language description of elements
            html: HTML content to search
            url: URL to fetch and analyze

        Returns:
            List of selector recommendations with confidence scores
        """
        return self.selector_finder.find(
            description=description,
            html=html,
            url=url
        )

    def reset_conversation(self):
        """Reset conversation history and start fresh."""
        self.conversation_history = []
        self.generated_code = None

    def export_scraper(
        self,
        format: str = "python",
        include_comments: bool = True
    ) -> str:
        """
        Export generated scraper in various formats.

        Args:
            format: Export format ("python", "jupyter", "module")
            include_comments: Whether to include explanatory comments

        Returns:
            Formatted scraper code
        """
        if not self.generated_code:
            raise ValueError("No scraper to export. Generate one first.")

        if format == "python":
            return self._format_python(self.generated_code, include_comments)
        elif format == "jupyter":
            return self._format_jupyter(self.generated_code)
        elif format == "module":
            return self._format_module(self.generated_code, include_comments)
        else:
            raise ValueError(f"Unknown export format: {format}")

    def _format_python(self, code: str, include_comments: bool) -> str:
        """Format as standalone Python script"""
        if include_comments:
            header = '''"""
Botasaurus Scraper
==================
Generated by AI Copilot

Run with: python scraper.py
"""

'''
            return header + code
        return code

    def _format_jupyter(self, code: str) -> str:
        """Format as Jupyter notebook JSON"""
        notebook = {
            "cells": [
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": ["# Botasaurus Scraper\\n", "Generated by AI Copilot"]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": code.split("\\n")
                }
            ],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }
        return json.dumps(notebook, indent=2)

    def _format_module(self, code: str, include_comments: bool) -> str:
        """Format as importable module"""
        # Similar to Python format but structured for imports
        return self._format_python(code, include_comments)
