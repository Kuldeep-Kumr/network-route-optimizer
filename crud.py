"""Database operations (thin layer over SQLAlchemy)."""

from datetime import datetime

from sqlalchemy import and_, delete, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

import models
import schemas


# --- Node ---


def create_node(db: Session, node: schemas.NodeCreate) -> models.Node:
    db_node = models.Node(name=node.name)
    db.add(db_node)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(db_node)
    return db_node


def get_nodes(db: Session, skip: int = 0, limit: int = 100) -> list[models.Node]:
    stmt = select(models.Node).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def get_node(db: Session, node_id: int) -> models.Node | None:
    return db.get(models.Node, node_id)


def get_node_by_name(db: Session, name: str) -> models.Node | None:
    stmt = select(models.Node).where(models.Node.name == name)
    return db.scalars(stmt).first()


def delete_node(db: Session, node_id: int) -> bool:
    node = db.get(models.Node, node_id)
    if node is None:
        return False
    db.execute(
        delete(models.Edge).where(
            or_(
                models.Edge.source_id == node_id,
                models.Edge.destination_id == node_id,
            )
        )
    )
    db.delete(node)
    db.commit()
    return True


# --- Edge ---


def create_edge(
    db: Session, *, source_id: int, destination_id: int, latency: float
) -> models.Edge:
    db_edge = models.Edge(
        source_id=source_id,
        destination_id=destination_id,
        latency=latency,
    )
    db.add(db_edge)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(db_edge)
    return db_edge


def get_edges(db: Session, skip: int = 0, limit: int = 100) -> list[models.Edge]:
    stmt = (
        select(models.Edge)
        .options(
            joinedload(models.Edge.source),
            joinedload(models.Edge.destination),
        )
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(stmt).unique().all())


def get_all_nodes(db: Session) -> list[models.Node]:
    return list(db.scalars(select(models.Node)).all())


def get_all_edges(db: Session) -> list[models.Edge]:
    return list(db.scalars(select(models.Edge)).all())


def get_edge(db: Session, edge_id: int) -> models.Edge | None:
    stmt = (
        select(models.Edge)
        .options(
            joinedload(models.Edge.source),
            joinedload(models.Edge.destination),
        )
        .where(models.Edge.id == edge_id)
    )
    return db.scalars(stmt).unique().first()


def check_duplicate_edge(
    db: Session, source_id: int, destination_id: int
) -> models.Edge | None:
    stmt = select(models.Edge).where(
        models.Edge.source_id == source_id,
        models.Edge.destination_id == destination_id,
    )
    return db.scalars(stmt).first()


def delete_edge(db: Session, edge_id: int) -> bool:
    edge = db.get(models.Edge, edge_id)
    if edge is None:
        return False
    db.delete(edge)
    db.commit()
    return True


# --- Route history ---


def create_history(
    db: Session, entry: schemas.RouteHistoryCreate
) -> models.RouteHistory:
    row = models.RouteHistory(
        source=entry.source,
        destination=entry.destination,
        total_latency=entry.total_latency,
        path=entry.path,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_history(
    db: Session,
    *,
    source: str | None = None,
    destination: str | None = None,
    limit: int = 100,
    created_after: datetime | None = None,
    created_before: datetime | None = None,
) -> list[models.RouteHistory]:
    stmt = select(models.RouteHistory)
    conditions = []
    if source is not None:
        conditions.append(models.RouteHistory.source == source)
    if destination is not None:
        conditions.append(models.RouteHistory.destination == destination)
    if created_after is not None:
        conditions.append(models.RouteHistory.created_at >= created_after)
    if created_before is not None:
        conditions.append(models.RouteHistory.created_at <= created_before)
    if conditions:
        stmt = stmt.where(and_(*conditions))
    stmt = stmt.order_by(models.RouteHistory.created_at.desc()).limit(limit)
    return list(db.scalars(stmt).all())
