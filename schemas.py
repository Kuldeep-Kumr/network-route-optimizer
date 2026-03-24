"""Pydantic schemas for API request and response bodies."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class NodeCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class NodeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class EdgeCreate(BaseModel):
    source_name: str = Field(..., min_length=1, max_length=255)
    destination_name: str = Field(..., min_length=1, max_length=255)
    latency: float

    @field_validator("latency")
    @classmethod
    def latency_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Latency must be greater than 0")
        return v


class EdgeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_name: str
    destination_name: str
    latency: float


class RouteRequest(BaseModel):
    source: str = Field(..., min_length=1, max_length=255)
    destination: str = Field(..., min_length=1, max_length=255)


class RouteResponse(BaseModel):
    total_latency: float
    path: list[str]


class RouteHistoryCreate(BaseModel):
    source: str = Field(..., min_length=1, max_length=255)
    destination: str = Field(..., min_length=1, max_length=255)
    total_latency: float
    path: list[str]


class RouteHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source: str
    destination: str
    total_latency: float
    path: list[str]
    created_at: datetime
