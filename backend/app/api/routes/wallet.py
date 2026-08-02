import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.exceptions.base import BusinessException
from app.models.user import User
from app.schemas.api import TransactionResponse, WalletBalanceResponse
from app.services.transaction_service import TransactionService
from app.services.wallet_service import WalletService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/wallet", tags=["Wallet"])


@router.get(
    "",
    response_model=WalletBalanceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Wallet Balance",
    description="Return current wallet balance for the authenticated user.",
)
def get_wallet_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WalletBalanceResponse:
    try:
        wallet_service = WalletService(db)
        balance = wallet_service.get_balance(current_user.id)
        return WalletBalanceResponse(balance=balance)
    except BusinessException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except Exception as e:
        logger.exception("Error getting wallet balance: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred")


@router.get(
    "/transactions",
    response_model=List[TransactionResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Transaction History",
    description="Return transaction history statement for the authenticated user's wallet.",
)
def get_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[TransactionResponse]:
    try:
        wallet_service = WalletService(db)
        wallet = wallet_service._get_wallet_by_user(current_user.id)
        tx_service = TransactionService(db)
        transactions = tx_service.get_transaction_history(wallet.id, skip=skip, limit=limit)
        return [TransactionResponse.model_validate(t) for t in transactions]
    except BusinessException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except Exception as e:
        logger.exception("Error getting transactions: %s", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred")
