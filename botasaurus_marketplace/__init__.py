"""
Botasaurus API Marketplace
===========================

Monetize scraped data through public APIs.

Features:
- API catalog and discovery
- Rate limiting per plan
- Usage tracking and billing
- Developer dashboard
- Revenue sharing
"""

__version__ = "0.1.0"

from .api_gateway import APIGateway
from .auth_manager import AuthManager
from .billing import BillingManager

__all__ = ["APIGateway", "AuthManager", "BillingManager"]
