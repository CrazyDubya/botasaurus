"""
Code Generator
==============

Generates Botasaurus scraper code from natural language and page analysis.
"""

from typing import Dict, List, Any, Optional
import re
from .prompts import (
    build_code_generation_prompt,
    build_refinement_prompt,
    build_explanation_prompt
)


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
        """
        Generate scraper code from prompt and analysis.

        Returns dict with code, explanation, selectors, warnings.
        """
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
        try:
            generated_text = self.llm_client.complete(
                messages=messages,
                temperature=0.3,  # Lower for more consistent code
                max_tokens=2000
            )
        except Exception as e:
            return {
                "code": "",
                "explanation": f"Error generating code: {str(e)}",
                "selectors": [],
                "warnings": [str(e)]
            }

        # Extract code from response
        code = self._extract_code(generated_text)

        # Generate explanation
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
        """Refine existing code based on user feedback"""

        messages = build_refinement_prompt(
            current_code=current_code,
            refinement_request=refinement_prompt,
            conversation_history=conversation_history
        )

        try:
            generated_text = self.llm_client.complete(
                messages=messages,
                temperature=0.3,
                max_tokens=2000
            )
        except Exception as e:
            return {
                "code": current_code,
                "explanation": f"Error refining code: {str(e)}",
                "changes": []
            }

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
        # Remove markdown code blocks if present
        code_block_pattern = r'```(?:python)?\n(.*?)\n```'
        matches = re.findall(code_block_pattern, text, re.DOTALL)

        if matches:
            return matches[0].strip()

        # If no code block, try to extract just the code part
        # Look for imports as start marker
        if 'from botasaurus import' in text or 'import botasaurus' in text:
            # Find first import line
            lines = text.split('\n')
            start_idx = 0
            for i, line in enumerate(lines):
                if 'import' in line and ('botasaurus' in line or 'bs4' in line):
                    start_idx = i
                    break

            # Take everything from first import onwards
            code_lines = lines[start_idx:]
            return '\n'.join(code_lines).strip()

        # If still nothing, return as-is
        return text.strip()

    def _extract_selectors(self, code: str) -> List[str]:
        """Extract CSS/XPath selectors from code"""
        selectors = []

        # CSS selectors (quoted strings starting with # or .)
        css_pattern = r'["\']([#.][\w\-]+(?:[\s>+~][\w\-#.]+)*)["\']'
        selectors.extend(re.findall(css_pattern, code))

        # Element selectors (tag names)
        tag_pattern = r'["\']([a-z][a-z0-9]*(?:\[[^\]]+\])?)["\']'
        selectors.extend(re.findall(tag_pattern, code))

        # XPath selectors
        xpath_pattern = r'["\'](//.+?)["\']'
        selectors.extend(re.findall(xpath_pattern, code))

        # Remove duplicates and return
        return list(set(selectors))[:10]  # Top 10

    def _check_warnings(self, code: str) -> List[str]:
        """Check for potential issues in generated code"""
        warnings = []

        if 'sleep(' in code or 'time.sleep' in code:
            warnings.append("Code uses sleep() - consider using wait_for_element() instead")

        if 'find_elements' in code and 'if' not in code and 'for' not in code:
            warnings.append("Using find_elements without checking if elements exist")

        if '@browser' in code and 'try' not in code:
            warnings.append("No error handling found - consider adding try/except blocks")

        if 'driver.get(' in code and 'wait' not in code.lower():
            warnings.append("No explicit waits found - page might not fully load")

        if 'human=True' not in code and '@browser' in code and ('click' in code or 'type' in code):
            warnings.append("Consider using human=True for clicks/typing to avoid detection")

        return warnings

    def _generate_explanation(self, code: str, original_prompt: str) -> str:
        """Generate plain English explanation of code"""
        if not code or code.startswith("#"):
            return "Code generation failed or incomplete"

        try:
            messages = build_explanation_prompt(code, original_prompt)
            explanation = self.llm_client.complete(
                messages=messages,
                temperature=0.5,
                max_tokens=200
            )
            return explanation.strip()
        except:
            # Fallback to simple explanation
            if '@browser' in code:
                return "This scraper uses browser automation to extract data from the page."
            elif '@request' in code:
                return "This scraper uses HTTP requests to fetch and parse the page."
            elif '@task' in code:
                return "This task processes data without web scraping."
            return "This code performs the requested scraping task."

    def _identify_changes(self, old_code: str, new_code: str) -> List[str]:
        """Identify what changed between code versions"""
        import difflib

        old_lines = old_code.splitlines()
        new_lines = new_code.splitlines()

        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm=''
        ))

        changes = []
        for line in diff:
            if line.startswith('+') and not line.startswith('+++'):
                changes.append(f"Added: {line[1:].strip()}")
            elif line.startswith('-') and not line.startswith('---'):
                changes.append(f"Removed: {line[1:].strip()}")

        return changes[:10]  # Limit to top 10 changes
