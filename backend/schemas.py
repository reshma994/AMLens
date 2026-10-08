from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


RiskLevel = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]

ReasonCode = Literal[
    "CIRCULAR_FLOW",
    "RAPID_PASS_THROUGH",
]

AlertStatus = Literal[
    "OPEN",
    "UNDER_REVIEW",
    "DISMISSED",
]


class Transaction(BaseModel):
    transaction_id: str
    source: str
    target: str
    amount_minor: int = Field(gt=0, le=100_000_000_000)
    timestamp: datetime


class Reason(BaseModel):
    code: ReasonCode
    points: int
    transaction_ids: list[str]


class Account(BaseModel):
    account_id: str
    risk_score: int = Field(ge=0, le=100)
    risk_level: RiskLevel
    reasons: list[Reason]


class AnalysisOutput(BaseModel):
    engine_version: str
    accounts: list[Account]


class GraphNode(BaseModel):
    id: str


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    amount_minor: int
    timestamp: datetime


class Graph(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class Summary(BaseModel):
    total_accounts: int
    total_transactions: int
    total_volume_minor: int
    alert_count: int
    high_risk_accounts: int


class Alert(BaseModel):
    id: str
    account_id: str
    status: AlertStatus
    updated_at: datetime


class AnalysisResult(BaseModel):
    analysis_id: str
    created_at: datetime
    engine_version: str
    currency: Literal["INR"]
    summary: Summary
    accounts: list[Account]
    graph: Graph
    alerts: list[Alert]


class UploadResponse(BaseModel):
    analysis_id: str
    status: Literal["COMPLETED"]
    result_url: str


class UpdateAlertRequest(BaseModel):
    status: AlertStatus


class ErrorDetail(BaseModel):
    code: str
    message: str
    row: int | None = None
    field: str | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail