"""SQLAlchemy ORM models for the network graph."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import (
    JSON,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Node(Base):
    __tablename__ = "nodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    outgoing_edges: Mapped[list[Edge]] = relationship(
        "Edge",
        foreign_keys="Edge.source_id",
        back_populates="source",
    )
    incoming_edges: Mapped[list[Edge]] = relationship(
        "Edge",
        foreign_keys="Edge.destination_id",
        back_populates="destination",
    )


class Edge(Base):
    __tablename__ = "edges"

    __table_args__ = (
        CheckConstraint("latency > 0", name="ck_edges_latency_positive"),
        UniqueConstraint(
            "source_id", "destination_id", name="uq_edges_source_destination"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("nodes.id"), nullable=False, index=True
    )
    destination_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("nodes.id"), nullable=False, index=True
    )
    latency: Mapped[float] = mapped_column(Float, nullable=False)

    source: Mapped[Node] = relationship(
        "Node",
        foreign_keys=[source_id],
        back_populates="outgoing_edges",
    )
    destination: Mapped[Node] = relationship(
        "Node",
        foreign_keys=[destination_id],
        back_populates="incoming_edges",
    )

    @property
    def source_name(self) -> str:
        return self.source.name

    @property
    def destination_name(self) -> str:
        return self.destination.name


class RouteHistory(Base):
    __tablename__ = "route_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(255), nullable=False)
    destination: Mapped[str] = mapped_column(String(255), nullable=False)
    total_latency: Mapped[float] = mapped_column(Float, nullable=False)
    path: Mapped[Any] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
