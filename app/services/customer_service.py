import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import CustomerNotFoundError, DuplicateEmailError
from app.dao.customer_dao import CustomerDAO
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._customer_dao = CustomerDAO(session)

    async def create_customer(self, payload: CustomerCreate) -> Customer:
        existing_customer = await self._customer_dao.get_by_email(payload.email)
        if existing_customer is not None:
            raise DuplicateEmailError("A customer with this email already exists.")

        customer = Customer(
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=payload.email,
            phone_number=payload.phone_number,
            date_of_birth=payload.date_of_birth,
            address=payload.address,
            account_status=payload.account_status,
            credit_score=payload.credit_score,
        )

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
            existing_customer = await self._customer_dao.get_by_email(payload.email)
            if existing_customer is not None and existing_customer.id != customer_id:
                raise DuplicateEmailError("A customer with this email already exists.")

        update_data = payload.model_dump(exclude_unset=True)
        for field_name, value in update_data.items():
            setattr(customer, field_name, value)

        try:
            saved_customer = await self._customer_dao.save(customer)
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            raise DuplicateEmailError("A customer with this email already exists.") from exc

        return saved_customer

    async def delete_customer(self, customer_id: uuid.UUID) -> None:
        customer = await self.get_customer(customer_id)
        await self._customer_dao.soft_delete(customer)
        await self._session.commit()
