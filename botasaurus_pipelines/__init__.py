"""
Botasaurus Data Pipelines
==========================

ETL and data orchestration framework.

Features:
- Visual pipeline builder
- 20+ data connectors
- Transformations and enrichments
- Scheduling and monitoring
- Data quality checks
"""

__version__ = "0.1.0"

from .pipeline import Pipeline
from .scheduler import PipelineScheduler
from .monitoring import PipelineMonitor

__all__ = ["Pipeline", "PipelineScheduler", "PipelineMonitor"]
