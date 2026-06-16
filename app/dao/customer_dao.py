import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer


class CustomerDAO:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, customer: Customer) -> Customer:
        self._session.add(customer)
        await self._session.flush()
        await self._session.refresh(customer)
        return customer

    async def list_customers(self) -> list[Customer]:
        statement = (
            select(Customer)
            .where(Customer.deleted_at.is_(None))
            .order_by(Customer.created_at.desc())
        )
        result = await self._session.scalars(statement)
        return list(result.all())

    async def get_by_id(self, customer_id: uuid.UUID) -> Customer | None:
        statement = select(Customer).where(
            Customer.id == customer_id,
            Customer.deleted_at.is_(None),
        )
        result = await self._session.scalars(statement)
        return result.one_or_none()

    async def get_by_email(self, email: str) -> Customer | None:
        statement = select(Customer).where(
            Customer.email == email,
            Customer.deleted_at.is_(None),
        )
        result = await self._session.scalars(statement)
        return result.one_or_none()

    async def soft_delete(self, customer: Customer) -> Customer:
        customer.deleted_at = datetime.now(UTC)
        await self._session.flush()
        return customer
