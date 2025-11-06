"""
Botasaurus Competitive Intelligence
====================================

Pre-built intelligence modules and dashboards.

Showcases:
- Competitor monitoring
- Price tracking
- Review analysis
- Job market intelligence
"""

__version__ = "0.1.0"

from .competitor_monitor import CompetitorMonitor
from .price_tracker import PriceTracker
from .review_analyzer import ReviewAnalyzer

__all__ = ["CompetitorMonitor", "PriceTracker", "ReviewAnalyzer"]
