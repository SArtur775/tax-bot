# services/database.py
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User, Calculation, Subscription
from database.engine import session_maker
from datetime import datetime
from typing import Optional, List

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self):
        logger.info("DatabaseService initialized with async support")
    
    # === USER METHODS ===
    async def get_or_create_user(self, user_id: int, username: str = None, 
                               first_name: str = None, last_name: str = None) -> User:
        """Получить пользователя или создать нового (асинхронно)"""
        async with session_maker() as session:
            result = await session.execute(
                select(User).where(User.user_id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                user = User(
                    user_id=user_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name
                )
                session.add(user)
                await session.commit()
                await session.refresh(user)
                logger.info(f"Created new user: {user_id}")
            
            return user
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """Получить пользователя по ID (асинхронно)"""
        async with session_maker() as session:
            result = await session.execute(
                select(User).where(User.user_id == user_id)
            )
            return result.scalar_one_or_none()
    
    # === CALCULATION METHODS ===
    async def save_calculation(self, user_id: int, calc_type: str, income: float, 
                             expenses: float, result_data: dict, additional_data: dict = None) -> Calculation:
        """Сохранить расчет в базу (асинхронно)"""
        async with session_maker() as session:
            calculation = Calculation(
                user_id=user_id,
                calc_type=calc_type,
                income=income,
                expenses=expenses,
                result_data=result_data,
                additional_data=additional_data or {}
            )
            session.add(calculation)
            await session.commit()
            await session.refresh(calculation)
            logger.info(f"Saved calculation for user {user_id}, type: {calc_type}")
            return calculation
    
    async def get_user_calculations(self, user_id: int, limit: int = 10) -> List[Calculation]:
        """Получить историю расчетов пользователя (асинхронно)"""
        async with session_maker() as session:
            result = await session.execute(
                select(Calculation)
                .where(Calculation.user_id == user_id)
                .order_by(Calculation.created_at.desc())
                .limit(limit)
            )
            calculations = result.scalars().all()
            return calculations
    
    async def get_calculations_count(self, user_id: int) -> int:
        """Получить количество расчетов пользователя (асинхронно)"""
        async with session_maker() as session:
            result = await session.execute(
                select(Calculation).where(Calculation.user_id == user_id)
            )
            calculations = result.scalars().all()
            return len(calculations)
    
    # === STATISTICS ===
    async def get_user_stats(self, user_id: int) -> dict:
        """Получить статистику пользователя (асинхронно)"""
        total_calculations = await self.get_calculations_count(user_id)
        
        calculations = await self.get_user_calculations(user_id, limit=50)
        calc_types = {}
        for calc in calculations:
            calc_types[calc.calc_type] = calc_types.get(calc.calc_type, 0) + 1
        
        return {
            'total_calculations': total_calculations,
            'calc_types': calc_types,
            'is_premium': False  # Пока всегда False
        }