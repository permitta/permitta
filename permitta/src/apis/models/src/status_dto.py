from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class StatusLabelsDto(BaseModel):
    id: str = Field()
    version: Optional[str] = None


class StatusTrinoBundleMetricsDto(BaseModel):
    timer_rego_data_parse_ns: int = Field()
    timer_rego_module_compile_ns: int = Field()
    timer_rego_module_parse_ns: int = Field()


class StatusPlatformBundleDto(BaseModel):
    active_revision: Optional[str] = None
    last_request: Optional[datetime] = None
    last_successful_request: Optional[datetime] = None
    last_successful_download: Optional[datetime] = None
    last_successful_activation: Optional[datetime] = None
    metrics: Optional[StatusTrinoBundleMetricsDto] = None
    name: str = Field()
    size: Optional[int] = None
    type: Optional[str] = None


class StatusBundlesDto(BaseModel):
    trino: StatusPlatformBundleDto = Field()


class StatusDecisionLogsMetricsDto(BaseModel):
    counter_decision_logs_dropped: str = Field()
    decision_logs_nd_builtin_cache_dropped: str = Field()


class StatusDecisionLogsDto(BaseModel):
    code: str = Field()
    message: str = Field()
    http_code: str = Field()
    metrics: StatusDecisionLogsMetricsDto = Field()


class StatusDto(BaseModel):
    labels: StatusLabelsDto = Field()
    bundles: Optional[StatusBundlesDto] = Field()
    decision_logs: Optional[StatusDecisionLogsDto] = None
