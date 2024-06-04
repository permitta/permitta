import datetime
from dataclasses import dataclass


@dataclass
class DecisionLogSoftwareStackDto:
    trinoVersion: str


@dataclass
class DecisionLogIdentityDto:
    groups: list[str]
    user: str


@dataclass
class DecisionLogContextDto:
    identity: DecisionLogIdentityDto
    softwareStack: DecisionLogSoftwareStackDto


@dataclass
class DecisionLogActionDto:
    operation: str


@dataclass
class DecisionLogInputDto:
    action: DecisionLogActionDto
    context: DecisionLogContextDto


@dataclass
class DecisionLogResultDto:
    expression: str


@dataclass
class DecisionLogDto:
    decision_id: str
    path: str
    input: DecisionLogInputDto
    result: bool | DecisionLogResultDto
    timestamp: datetime.datetime
