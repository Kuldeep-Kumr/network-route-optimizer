from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import crud
import schemas
from database import get_db

router = APIRouter()


@router.get("/", response_model=list[schemas.EdgeResponse])
def list_edges(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_edges(db, skip=skip, limit=limit)


@router.get("/{edge_id}", response_model=schemas.EdgeResponse)
def read_edge(edge_id: int, db: Session = Depends(get_db)):
    edge = crud.get_edge(db, edge_id)
    if edge is None:
        raise HTTPException(status_code=404, detail="Edge not found")
    return edge


@router.post("/", response_model=schemas.EdgeResponse, status_code=201)
def create_edge(payload: schemas.EdgeCreate, db: Session = Depends(get_db)):
    src = crud.get_node_by_name(db, payload.source_name)
    if src is None:
        raise HTTPException(
            status_code=404,
            detail=f"No node named {payload.source_name!r} (source)",
        )
    dst = crud.get_node_by_name(db, payload.destination_name)
    if dst is None:
        raise HTTPException(
            status_code=404,
            detail=f"No node named {payload.destination_name!r} (destination)",
        )
    if crud.check_duplicate_edge(db, src.id, dst.id) is not None:
        raise HTTPException(
            status_code=409,
            detail="An edge between this source and destination already exists",
        )
    try:
        return crud.create_edge(
            db,
            source_id=src.id,
            destination_id=dst.id,
            latency=payload.latency,
        )
    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="An edge between this source and destination already exists",
        ) from None


@router.delete("/{edge_id}", status_code=204)
def delete_edge(edge_id: int, db: Session = Depends(get_db)):
    if not crud.delete_edge(db, edge_id):
        raise HTTPException(status_code=404, detail="Edge not found")
