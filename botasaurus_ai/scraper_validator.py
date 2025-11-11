"""
Scraper Validator
=================

Validates generated scraper code for correctness and best practices.
"""

from typing import Dict, List, Any, Optional
import ast
import re


class ScraperValidator:
    """Validates scraper code for syntax, structure, and best practices"""

    def validate(
        self,
        code: str,
        url: Optional[str] = None,
        test_execution: bool = False
    ) -> Dict[str, Any]:
        """
        Validate scraper code.

        Args:
            code: Python code to validate
            url: Optional URL to test against
            test_execution: Whether to actually run the code (dangerous!)

        Returns:
            - valid: bool
            - errors: List of errors
            - warnings: List of warnings
            - fixable: bool
        """
        errors = []
        warnings = []

        # 1. Syntax check
        syntax_errors = self._check_syntax(code)
        errors.extend(syntax_errors)

        # 2. Import check
        import_errors = self._check_imports(code)
        errors.extend(import_errors)

        # 3. Decorator check
        decorator_warnings = self._check_decorators(code)
        warnings.extend(decorator_warnings)

        # 4. Security check
        security_errors = self._check_security(code)
        errors.extend(security_errors)

        # 5. Best practices
        best_practice_warnings = self._check_best_practices(code)
        warnings.extend(best_practice_warnings)

        # 6. Structure validation
        structure_errors = self._check_structure(code)
        errors.extend(structure_errors)

        # 7. Optional: Test execution (disabled by default for security)
        if test_execution and url and not errors:
            exec_result = self._test_execution(code, url)
            if not exec_result["success"]:
                errors.append(exec_result["error"])

        valid = len(errors) == 0
        fixable = self._is_fixable(errors)

        return {
            "valid": valid,
            "errors": errors,
            "warnings": warnings,
            "fixable": fixable,
            "error_count": len(errors),
            "warning_count": len(warnings)
        }

    def _check_syntax(self, code: str) -> List[str]:
        """Check Python syntax"""
        try:
            ast.parse(code)
            return []
        except SyntaxError as e:
            return [f"Syntax error at line {e.lineno}: {e.msg}"]
        except Exception as e:
            return [f"Parse error: {str(e)}"]

    def _check_imports(self, code: str) -> List[str]:
        """Check required imports are present"""
        errors = []

        required_imports = {
            '@browser': 'from botasaurus import browser',
            '@request': 'from botasaurus import request',
            '@task': 'from botasaurus import task'
        }

        for decorator, import_line in required_imports.items():
            if decorator in code and import_line not in code:
                # Check for alternative import styles
                alt_import = 'import botasaurus'
                if alt_import not in code:
                    errors.append(f"Missing import for {decorator}: {import_line}")

        return errors

    def _check_decorators(self, code: str) -> List[str]:
        """Check decorator usage"""
        warnings = []

        try:
            tree = ast.parse(code)
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

            if not functions:
                warnings.append("No functions found in code")
                return warnings

            for func in functions:
                # Check if function has a decorator
                if not func.decorator_list:
                    warnings.append(f"Function '{func.name}' has no Botasaurus decorator")
                    continue

                # Check parameter count based on decorator type
                if '@browser' in code:
                    if len(func.args.args) < 2:
                        warnings.append(
                            f"@browser function '{func.name}' should have (driver, data) parameters"
                        )
                elif '@request' in code:
                    if len(func.args.args) < 2:
                        warnings.append(
                            f"@request function '{func.name}' should have (request, data) parameters"
                        )
                elif '@task' in code:
                    if len(func.args.args) < 1:
                        warnings.append(
                            f"@task function '{func.name}' should have (data) parameter"
                        )

        except Exception as e:
            warnings.append(f"Could not analyze decorators: {str(e)}")

        return warnings

    def _check_security(self, code: str) -> List[str]:
        """Check for dangerous code patterns"""
        errors = []

        dangerous_patterns = [
            (r'\beval\s*\(', "Use of eval() is dangerous"),
            (r'\bexec\s*\(', "Use of exec() is dangerous"),
            (r'__import__', "Dynamic imports are not allowed"),
            (r'os\.system', "Shell commands are not allowed"),
            (r'subprocess\.', "Subprocess calls are not allowed"),
            (r'open\s*\([^)]*["\']w', "File writing is not allowed"),
        ]

        for pattern, message in dangerous_patterns:
            if re.search(pattern, code):
                errors.append(f"Security violation: {message}")

        return errors

    def _check_best_practices(self, code: str) -> List[str]:
        """Check code follows best practices"""
        warnings = []

        # Check for error handling
        if '@browser' in code or '@request' in code:
            if 'try' not in code and 'except' not in code:
                warnings.append("No error handling found - add try/except blocks")

        # Check for return statement
        try:
            tree = ast.parse(code)
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

            for func in functions:
                # Check if function has return statement
                has_return = any(
                    isinstance(node, ast.Return) for node in ast.walk(func)
                )
                if not has_return:
                    warnings.append(f"Function '{func.name}' should return data")

        except:
            pass

        # Check for sleep usage (bad practice)
        if 'sleep(' in code or 'time.sleep' in code:
            warnings.append("Avoid sleep() - use wait_for_element() instead")

        # Check for human parameter in browser automation
        if '@browser' in code:
            if ('click(' in code or 'type(' in code) and 'human=True' not in code:
                warnings.append("Use human=True for clicks/typing to avoid bot detection")

        # Check for explicit waits
        if '@browser' in code and 'driver.get(' in code:
            if 'wait_for' not in code.lower():
                warnings.append("Use explicit waits (wait_for_element) after page loads")

        return warnings

    def _check_structure(self, code: str) -> List[str]:
        """Check code structure"""
        errors = []

        # Must have at least one function
        try:
            tree = ast.parse(code)
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

            if not functions:
                errors.append("Code must contain at least one function")

        except:
            pass  # Syntax error already caught

        # Must have at least one Botasaurus decorator
        if not any(decorator in code for decorator in ['@browser', '@request', '@task']):
            errors.append("Code must use at least one Botasaurus decorator (@browser, @request, or @task)")

        return errors

    def _is_fixable(self, errors: List[str]) -> bool:
        """Check if errors are auto-fixable"""
        fixable_keywords = [
            'Missing import',
            'Indentation',
            'expected',
            'should have',
            'parameters'
        ]

        if not errors:
            return False

        # If all errors contain fixable keywords
        return any(
            any(keyword in error for keyword in fixable_keywords)
            for error in errors
        )

    def _test_execution(self, code: str, url: str) -> Dict[str, Any]:
        """
        Test code execution (DISABLED for security).

        This would require sandboxing to be safe.
        """
        return {
            "success": False,
            "error": "Test execution is disabled for security reasons"
        }
