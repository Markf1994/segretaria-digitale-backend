from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.piano_segnaletica_orizzontale import (
    PianoSegnaleticaOrizzontaleCreate,
    PianoSegnaleticaOrizzontaleResponse,
    SegnaleticaOrizzontaleItemCreate,
    SegnaleticaOrizzontaleItemResponse,
    SegnaleticaOrizzontaleItemUpdate,
)
from app.crud import piano_segnaletica_orizzontale as crud

router = APIRouter(prefix="/piani-orizzontali", tags=["Piani Segnaletica Orizzontale"])


@router.post("/", response_model=PianoSegnaleticaOrizzontaleResponse)
def create_piano_route(data: PianoSegnaleticaOrizzontaleCreate, db: Session = Depends(get_db)):
    return crud.create_piano(db, data)


@router.get("/", response_model=list[PianoSegnaleticaOrizzontaleResponse])
def list_piani(
    search: str | None = None,
    anno: int | None = None,
    db: Session = Depends(get_db),
):
    return crud.get_piani(db, search=search, anno=anno)


@router.put("/{piano_id}", response_model=PianoSegnaleticaOrizzontaleResponse)
def update_piano_route(
    piano_id: str,
    data: PianoSegnaleticaOrizzontaleCreate,
    db: Session = Depends(get_db),
):
    db_obj = crud.update_piano(db, piano_id, data)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Piano not found")
    return db_obj


@router.delete("/{piano_id}")
def delete_piano_route(piano_id: str, db: Session = Depends(get_db)):
    db_obj = crud.delete_piano(db, piano_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Piano not found")
    return {"ok": True}


@router.post("/{piano_id}/items", response_model=SegnaleticaOrizzontaleItemResponse)
def add_item_route(
    piano_id: str,
    data: SegnaleticaOrizzontaleItemCreate,
    db: Session = Depends(get_db),
):
    item = crud.add_item(db, piano_id, data)
    if not item:
        raise HTTPException(status_code=404, detail="Piano not found")
    return item


@router.put("/items/{item_id}", response_model=SegnaleticaOrizzontaleItemResponse)
def update_item_route(
    item_id: str,
    data: SegnaleticaOrizzontaleItemUpdate,
    db: Session = Depends(get_db),
):
    item = crud.update_item(db, item_id, data)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.delete("/items/{item_id}")
def delete_item_route(item_id: str, db: Session = Depends(get_db)):
    item = crud.delete_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"ok": True}
