"""
Payment database for storing payment details.
Use a in-memory database to mock the behavior of a real database.
"""
from typing import Dict, Optional
from .datamodels import PaymentResponse


class PaymentDatabase:
    # In-memory storage: payment_id -> PaymentResponse
    _payments: Dict[str, PaymentResponse] = {}

    @classmethod
    def save_payment(cls, payment: PaymentResponse) -> None:
        cls._payments[payment.payment_id] = payment

    @classmethod
    def get_payment(cls, payment_id: str) -> Optional[PaymentResponse]:
        return cls._payments.get(payment_id)

    @classmethod
    def payment_exists(cls, payment_id: str) -> bool:
        return payment_id in cls._payments

    @classmethod
    def clear_all(cls) -> None:
        cls._payments.clear()

    @classmethod
    def delete_payment(cls, payment_id: str) -> None:
        if payment_id not in cls._payments:
            return
        del cls._payments[payment_id]
    
    @classmethod
    def get_all_payments(cls) -> Dict[str, PaymentResponse]:
        return cls._payments.copy()
    
    @classmethod
    def count(cls) -> int:
        return len(cls._payments)
