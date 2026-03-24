from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import crud
import schemas
from database import get_db

router = APIRouter()

_DUPLICATE_NAME_DETAIL = "A node with this name already exists"


@router.get("/", response_model=list[schemas.NodeResponse])
def list_nodes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_nodes(db, skip=skip, limit=limit)


@router.post("/", response_model=schemas.NodeResponse, status_code=201)
def create_node(payload: schemas.NodeCreate, db: Session = Depends(get_db)):
    if crud.get_node_by_name(db, payload.name) is not None:
        raise HTTPException(status_code=409, detail=_DUPLICATE_NAME_DETAIL)
    try:
        return crud.create_node(db, payload)
    except IntegrityError:
        raise HTTPException(status_code=409, detail=_DUPLICATE_NAME_DETAIL) from None


@router.delete("/{node_id}", status_code=204)
def delete_node(node_id: int, db: Session = Depends(get_db)):
    if not crud.delete_node(db, node_id):
        raise HTTPException(status_code=404, detail="Node not found")
