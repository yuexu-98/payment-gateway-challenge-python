from typing import Dict
from fastapi import FastAPI, HTTPException
from .datamodels import PaymentRequest, PaymentResponse
from .payment_processor import PaymentProcessor
from pydantic import ValidationError

app = FastAPI()

@app.get("/")
async def ping() -> Dict[str, str]:
    return {"app": "payment-gateway-api"}

"""
This endpoint is used to create a payment.
Parameters:
- payment_request: PaymentRequest
Returns:
- PaymentResponse
Exceptions:
- HTTPException: 500 Internal Server Error
"""
# POST /payments
@app.post("/payments")
async def create_payment(payment_request: PaymentRequest) -> PaymentResponse:
    try:
        return PaymentProcessor.process_payment(payment_request)
    except ValueError as e:
        # Request validation / simulator 4xx mapping
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        # Bank simulator unavailable
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

"""
This endpoint is used to get the details of a payment.
Parameters:
- payment_id: str
Returns:
- PaymentResponse
Exceptions:
- HTTPException: 500 Internal Server Error
- Exception: Any other exception
"""
# GET /payments/{payment_id}
@app.get("/payments/{payment_id}")
async def get_payment(payment_id: str) -> PaymentResponse:
    try:
        return PaymentProcessor.get_payment_details(payment_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Payment not found")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )