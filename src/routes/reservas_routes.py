import random

from fastapi import HTTPException
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import select

from src.config.database import get_session
from src.models.reservas_model import Reserva
from src.models.voos_model import Voo

reservas_router = APIRouter(prefix="/reservas")


@reservas_router.get("/{id_voo}")
def lista_reservas_voo(id_voo: int):
    with get_session() as session:
        statement = select(Reserva).where(Reserva.voo_id == id_voo)
        reservas = session.exec(statement).all()
        return reservas


@reservas_router.post("")
def cria_reserva(reserva: Reserva):
    with get_session() as session:
        voo = session.exec(select(Voo).where(Voo.id == reserva.voo_id)).first()

        if not voo:
            return JSONResponse(
                content={"message": f"Voo com id {reserva.voo_id} não encontrado."},
                status_code=404,
            )

        # TODO - Validar se existe uma reserva para o mesmo documento

        reserva_existente = (
            session.exec(
                select(Reserva).where(Reserva.documento == reserva.documento)
            ).first()
            )
        codigo_reserva = "".join(
            [str(random.randint(0, 999)).zfill(3) for _ in range(2)]
        )
        if reserva_existente:
            return JSONResponse(
                content={"message": f"Já existe uma reserva com este documento {reserva.voo_id}."},
                status_code=400,
            )

        reserva.codigo_reserva = codigo_reserva
        session.add(reserva)
        session.commit()
        session.refresh(reserva)
        return reserva


@reservas_router.post("/{codigo_reserva}/checkin/{num_poltrona}")
def checkin(codigo_reserva: str, num_poltrona: int):
    pass

    # TODO - Implementar reserva de poltrona
@reservas_router.post("/{codigo_reserva}/checkin/{num_poltrona}")
def checkin(codigo_reserva: str, num_poltrona: int):
    with get_session() as session:
        reserva = session.exec(select(Reserva).where(Reserva.codigo_reserva == codigo_reserva)).first()
    
    if not reserva:
            return JSONResponse(
                content={"message": f"Reserva com código {codigo_reserva} não encontrada."},
                status_code=404,
            )

    if reserva.num_poltrona is not None:
            return JSONResponse(
                content={"message": f"Poltrona {num_poltrona} ocupada."},
                status_code=400,
            )
    
    # TODO - Implementar troca de reserva de poltrona

@reservas_router.patch("/{codigo_reserva}/checkin/{num_poltrona}")
def checkin(codigo_reserva: str, num_poltrona: int):
    with get_session() as session:
        reserva = session.exec(select(Reserva).where(Reserva.codigo_reserva == codigo_reserva)).first()

    if not reserva:
        raise HTTPException(status_code=404, detail=f"A reserva com o código {codigo_reserva} não foi encontrada.")

    if reserva.num_poltrona is not None:
        raise HTTPException(status_code=400, detail=f"Poltrona {num_poltrona} encontra-se ocupada.")

    reserva.num_poltrona = num_poltrona
    session.commit()
    session.refresh(reserva)

    return reserva
