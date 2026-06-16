import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.exceptions import CustomerNotFoundError, DuplicateEmailError
from app.schemas.customer import CustomerCreate, CustomerRead, CustomerUpdate
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["customers"])


def get_customer_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> CustomerService:
    return CustomerService(session)


@router.post("", response_model=CustomerRead, status_code=status.HTTP_201_CREATED)
async def create_customer(
    payload: CustomerCreate,
    service: Annotated[CustomerService, Depends(get_customer_service)],
) -> CustomerRead:
    try:
        return await service.create_customer(payload)
    except DuplicateEmailError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message) from exc


@router.get("", response_model=list[CustomerRead])
async def list_customers(
    service: Annotated[CustomerService, Depends(get_customer_service)],
) -> list[CustomerRead]:
    return await service.list_customers()


@router.get("/{customer_id}", response_model=CustomerRead)
async def get_customer(
    customer_id: uuid.UUID,
    service: Annotated[CustomerService, Depends(get_customer_service)],
) -> CustomerRead:
    try:
        return await service.get_customer(customer_id)
    except CustomerNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc


@router.put("/{customer_id}", response_model=CustomerRead)
async def update_customer(
    customer_id: uuid.UUID,
    payload: CustomerUpdate,
    service: Annotated[CustomerService, Depends(get_customer_service)],
) -> CustomerRead:
    try:
        return await service.update_customer(customer_id, payload)
    except CustomerNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    except DuplicateEmailError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message) from exc


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: uuid.UUID,
    service: Annotated[CustomerService, Depends(get_customer_service)],
) -> Response:
    try:
        await service.delete_customer(customer_id)
    except CustomerNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
