from datetime import datetime
from uuid import uuid4
import pycountry
from .datamodels import PaymentRequest, PaymentResponse, PaymentRequestValidator
from .payment_database import PaymentDatabase
import httpx

BANK_ENDPOINT = "http://localhost:8080/payments"


class PaymentProcessor:
    """
    Payment processor for handling payment requests and bank simulator communication.
    Uses PaymentDatabase for storing payment details.
    """
    @staticmethod
    def process_payment(payment_request: PaymentRequest) -> PaymentResponse:

        # STEP 1: Validate the payment request, reject if not a valid request
        if not PaymentRequestValidator.validate_payment_request(payment_request):
            payment_id = str(uuid4())
            rejected_response = PaymentResponse(
                payment_id=payment_id,
                status="Rejected",
                card_last_four=payment_request.card_number[-4:],    
                card_expiration_month=payment_request.card_expiration_month,
                card_expiration_year=payment_request.card_expiration_year,
                currency=payment_request.currency,
                amount=payment_request.amount
            )
            # Store rejected payment in database
            PaymentDatabase.save_payment(rejected_response)
            return rejected_response

        # STEP 2: Process the payment
        try:
            response = httpx.post(
                BANK_ENDPOINT,
                json=payment_request.model_dump()
            )
            data = response.json()
            auth = data.get("authorized")
            auth_code = data.get("authorization_code")
            if not auth or not auth_code:
                raise ValueError(f"Bank simulator returned an error: {data.get('error')}")

            # Use authorization_code as payment_id, or generate one if not provided
            payment_id = auth_code if auth_code else str(uuid4())
            
            payment_response = PaymentResponse(
                payment_id=payment_id,
                status="Authorized" if auth == True else "Declined",
                card_last_four=payment_request.card_number[-4:],
                card_expiration_month=payment_request.card_expiration_month,
                card_expiration_year=payment_request.card_expiration_year,
                currency=payment_request.currency,
                amount=payment_request.amount
            )
            
            # Store payment in database
            PaymentDatabase.save_payment(payment_response)
            
            return payment_response
        except Exception as e:
            raise Exception(e)

    @staticmethod
    def get_payment_details(payment_id: str) -> PaymentResponse:
        payment = PaymentDatabase.get_payment(payment_id)
        if payment is None:
            raise KeyError(f"Payment not found: {payment_id}")
        
        return payment

