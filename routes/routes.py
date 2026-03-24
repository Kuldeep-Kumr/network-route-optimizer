from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import crud
import graph
import schemas
from database import get_db

router = APIRouter()


@router.get("/history", response_model=list[schemas.RouteHistoryResponse])
def list_route_history(
    db: Session = Depends(get_db),
    source: str | None = None,
    destination: str | None = None,
    limit: int = 100,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
):
    return crud.get_history(
        db,
        source=source,
        destination=destination,
        limit=limit,
        created_after=date_from,
        created_before=date_to,
    )


@router.post("/shortest", response_model=schemas.RouteResponse)
def shortest_route(
    payload: schemas.RouteRequest, db: Session = Depends(get_db)
) -> schemas.RouteResponse:
    source_node = crud.get_node_by_name(db, payload.source)
    dest_node = crud.get_node_by_name(db, payload.destination)
    if source_node is None or dest_node is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid source or destination node",
        )

    nodes = crud.get_all_nodes(db)
    edges = crud.get_all_edges(db)
    id_to_name = {n.id: n.name for n in nodes}

    adj = graph.build_adjacency(
        [(e.source_id, e.destination_id, e.latency) for e in edges]
    )
    total, path_ids = graph.dijkstra_shortest_path(
        adj, source_node.id, dest_node.id
    )
    if total is None or path_ids is None:
        raise HTTPException(
            status_code=404,
            detail="No path exists between source and destination",
        )

    path_names = [id_to_name[i] for i in path_ids]
    crud.create_history(
        db,
        schemas.RouteHistoryCreate(
            source=payload.source,
            destination=payload.destination,
            total_latency=total,
            path=path_names,
        ),
    )
    return schemas.RouteResponse(total_latency=total, path=path_names)
