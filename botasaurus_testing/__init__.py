"""
Botasaurus Testing Framework
=============================

Browser automation testing leveraging anti-detection capabilities.

Features:
- Undetectable test automation
- Visual regression testing
- Network interception
- CI/CD integration
"""

__version__ = "0.1.0"

from .test_runner import TestRunner
from .assertions import BotasaurusAssertions

__all__ = ["TestRunner", "BotasaurusAssertions"]
