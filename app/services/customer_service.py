import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import CustomerNotFoundError, DuplicateEmailError
from app.dao.customer_dao import CustomerDAO
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.services.customer_factory import CustomerFactory
from app.services.customer_validator import CustomerValidator


class CustomerService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._customer_dao = CustomerDAO(session)
        self._customer_factory = CustomerFactory()
        self._customer_validator = CustomerValidator(self._customer_dao)

    async def create_customer(self, payload: CustomerCreate) -> Customer:
        await self._customer_validator.ensure_email_available(payload.email)
        customer = self._customer_factory.create_from_payload(payload)

        try:
            saved_customer = await self._customer_dao.save(customer)
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            raise DuplicateEmailError("A customer with this email already exists.") from exc

        return saved_customer

    async def list_customers(self) -> list[Customer]:
        return await self._customer_dao.list_customers()

    async def get_customer(self, customer_id: uuid.UUID) -> Customer:
        customer = await self._customer_dao.get_by_id(customer_id)
        if customer is None:
            raise CustomerNotFoundError("Customer not found.")
        return customer

    async def update_customer(self, customer_id: uuid.UUID, payload: CustomerUpdate) -> Customer:
        customer = await self.get_customer(customer_id)

        if payload.email is not None and payload.email != customer.email:
            await self._customer_validator.ensure_email_available(payload.email, customer_id)

        self._customer_factory.apply_update(customer, payload)

        try:
            saved_customer = await self._customer_dao.save(customer)
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            raise DuplicateEmailError("A customer with this email already exists.") from exc

        return saved_customer

    async def delete_customer(self, customer_id: uuid.UUID) -> None:
        customer = await self.get_customer(customer_id)
        customer.mark_deleted()
        await self._customer_dao.save(customer)
        await self._session.commit()
