from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerFactory:
    def create_from_payload(self, payload: CustomerCreate) -> Customer:
        return Customer(
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=payload.email,
            phone_number=payload.phone_number,
            date_of_birth=payload.date_of_birth,
            address=payload.address,
            account_status=payload.account_status,
            credit_score=payload.credit_score,
        )

    def apply_update(self, customer: Customer, payload: CustomerUpdate) -> Customer:
        for field_name in payload.model_fields_set:
            setattr(customer, field_name, getattr(payload, field_name))
        return customer
