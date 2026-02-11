"""SQLAlchemy TransactionRepository implementation."""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime
from decimal import Decimal
import uuid

from ...domain.entities.transaction import Transaction
from ...domain.repositories.transaction_repository import TransactionRepository
from ..database.models import TransactionModel


class SQLAlchemyTransactionRepository(TransactionRepository):
    """SQLAlchemy implementation of TransactionRepository."""
    
    def __init__(self, session: Session):
        self.session = session
    
    async def save(self, transaction: Transaction) -> Transaction:
        """Save transaction (create or update)."""
        if transaction.transaction_id:
            # Update existing
            model = self.session.query(TransactionModel).filter(
                TransactionModel.transaction_id == transaction.transaction_id
            ).first()
            
            if model:
                model.amount = transaction.amount
                model.category = transaction.category
                model.date = transaction.date
                model.note = transaction.note
            else:
                model = self._create_model(transaction)
                self.session.add(model)
        else:
            # Create new
            model = self._create_model(transaction)
            self.session.add(model)
        
        self.session.commit()
        self.session.refresh(model)
        
        return self._to_entity(model)
    
    async def get_by_id(self, transaction_id: str) -> Optional[Transaction]:
        """Get transaction by ID."""
        model = self.session.query(TransactionModel).filter(
            TransactionModel.transaction_id == transaction_id
        ).first()
        
        return self._to_entity(model) if model else None
    
    async def delete(self, transaction_id: str) -> bool:
        """Delete transaction by ID."""
        model = self.session.query(TransactionModel).filter(
            TransactionModel.transaction_id == transaction_id
        ).first()
        
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        
        return False
    
    async def get_recent(self, user_id: int, limit: int = 10) -> List[Transaction]:
        """Get recent transactions for user."""
        models = self.session.query(TransactionModel).filter(
            TransactionModel.user_id == user_id
        ).order_by(TransactionModel.date.desc()).limit(limit).all()
        
        return [self._to_entity(model) for model in models]
    
    async def get_by_date_range(
        self, 
        user_id: int, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Transaction]:
        """Get transactions within date range."""
        models = self.session.query(TransactionModel).filter(
            and_(
                TransactionModel.user_id == user_id,
                TransactionModel.date >= start_date,
                TransactionModel.date <= end_date
            )
        ).order_by(TransactionModel.date.desc()).all()
        
        return [self._to_entity(model) for model in models]
    
    async def get_by_category(self, user_id: int, category: str) -> List[Transaction]:
        """Get transactions by category."""
        models = self.session.query(TransactionModel).filter(
            and_(
                TransactionModel.user_id == user_id,
                TransactionModel.category == category
            )
        ).order_by(TransactionModel.date.desc()).all()
        
        return [self._to_entity(model) for model in models]
    
    async def get_income_total(
        self, 
        user_id: int, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Decimal:
        """Calculate total income for user."""
        query = self.session.query(func.sum(TransactionModel.amount)).filter(
            and_(
                TransactionModel.user_id == user_id,
                TransactionModel.amount > 0
            )
        )
        
        if start_date:
            query = query.filter(TransactionModel.date >= start_date)
        if end_date:
            query = query.filter(TransactionModel.date <= end_date)
        
        result = query.scalar()
        return Decimal(str(result)) if result else Decimal("0")
    
    async def get_expense_total(
        self, 
        user_id: int, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Decimal:
        """Calculate total expenses for user."""
        query = self.session.query(func.sum(TransactionModel.amount)).filter(
            and_(
                TransactionModel.user_id == user_id,
                TransactionModel.amount < 0
            )
        )
        
        if start_date:
            query = query.filter(TransactionModel.date >= start_date)
        if end_date:
            query = query.filter(TransactionModel.date <= end_date)
        
        result = query.scalar()
        # Return absolute value for expenses
        return abs(Decimal(str(result))) if result else Decimal("0")
    
    async def count_by_user(self, user_id: int) -> int:
        """Count transactions for user."""
        return self.session.query(func.count(TransactionModel.id)).filter(
            TransactionModel.user_id == user_id
        ).scalar()
    
    def _create_model(self, transaction: Transaction) -> TransactionModel:
        """Create database model from entity."""
        # Generate UUID if transaction_id is None
        transaction_id = transaction.transaction_id or str(uuid.uuid4())
        
        return TransactionModel(
            transaction_id=transaction_id,
            user_id=transaction.user_id,
            amount=transaction.amount,
            category=transaction.category,
            date=transaction.date,
            note=transaction.note,
            created_at=transaction.created_at
        )
    
    def _to_entity(self, model: TransactionModel) -> Transaction:
        """Convert database model to domain entity."""
        return Transaction(
            user_id=model.user_id,
            amount=Decimal(str(model.amount)),
            category=model.category,
            date=model.date,
            note=model.note,
            transaction_id=model.transaction_id
        )
