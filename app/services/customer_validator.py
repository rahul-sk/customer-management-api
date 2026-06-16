import uuid

from app.core.exceptions import DuplicateEmailError
from app.dao.customer_dao import CustomerDAO


class CustomerValidator:
    def __init__(self, customer_dao: CustomerDAO) -> None:
        self._customer_dao = customer_dao

    async def ensure_email_available(
        self,
        email: str,
        current_customer_id: uuid.UUID | None = None,
    ) -> None:
        existing_customer = await self._customer_dao.get_by_email(email)
        if existing_customer is None:
            return

        if current_customer_id is not None and existing_customer.id == current_customer_id:
            return

        raise DuplicateEmailError("A customer with this email already exists.")
