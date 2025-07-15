from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.dispositivo import DispositivoCreate, DispositivoResponse
from app.crud import dispositivo

router = APIRouter(prefix="/dispositivi", tags=["Dispositivi"])


@router.post("/", response_model=DispositivoResponse)
def create_dispositivo_route(data: DispositivoCreate, db: Session = Depends(get_db)):
    return dispositivo.create_dispositivo(db, data)


@router.get("/", response_model=list[DispositivoResponse])
def list_dispositivi(
    search: str | None = None,
    anno: int | None = None,
    db: Session = Depends(get_db),
):
    return dispositivo.get_dispositivi(db, search=search, anno=anno)


@router.put("/{dispositivo_id}", response_model=DispositivoResponse)
def update_dispositivo_route(dispositivo_id: str, data: DispositivoCreate, db: Session = Depends(get_db)):
    db_obj = dispositivo.update_dispositivo(db, dispositivo_id, data)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Dispositivo not found")
    return db_obj


@router.delete("/{dispositivo_id}")
def delete_dispositivo_route(dispositivo_id: str, db: Session = Depends(get_db)):
    db_obj = dispositivo.delete_dispositivo(db, dispositivo_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Dispositivo not found")
    return {"ok": True}
