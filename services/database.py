# services/database.py
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User, Calculation, Subscription
from database.engine import session_maker
from datetime import datetime, timedelta
from typing import Optional, List, Tuple

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

    # === LIMIT METHODS ===
    async def check_calculation_limit(self, user_id: int) -> Tuple[bool, int, int]:
        """Проверить лимит расчетов для пользователя (асинхронно)"""
        is_premium = await self.check_premium_access(user_id)
        
        if is_premium:
            return True, 0, 0  # Безлимитно для премиум
        
        # Для бесплатных пользователей
        today = datetime.utcnow().date()
        async with session_maker() as session:
            result = await session.execute(
                select(Calculation)
                .where(
                    Calculation.user_id == user_id,
                    Calculation.created_at >= today
                )
            )
            today_calculations = result.scalars().all()
        
        free_daily_limit = 5
        used_calculations = len(today_calculations)
        remaining = max(0, free_daily_limit - used_calculations)
        
        return remaining > 0, used_calculations, remaining

    async def get_today_calculations_count(self, user_id: int) -> int:
        """Получить количество расчетов сегодня (асинхронно)"""
        today = datetime.utcnow().date()
        async with session_maker() as session:
            result = await session.execute(
                select(Calculation)
                .where(
                    Calculation.user_id == user_id,
                    Calculation.created_at >= today
                )
            )
            calculations = result.scalars().all()
            return len(calculations)

    # === SUBSCRIPTION METHODS ===
    async def create_subscription(self, user_id: int, plan: str = 'premium', 
                                months: int = 1, payment_id: str = None) -> Subscription:
        """Создать подписку для пользователя (асинхронно)"""
        async with session_maker() as session:
            starts_at = datetime.utcnow()
            expires_at = starts_at + timedelta(days=30 * months)
            
            subscription = Subscription(
                user_id=user_id,
                plan=plan,
                status='active',
                starts_at=starts_at,
                expires_at=expires_at,
                payment_id=payment_id
            )
            
            # Обновляем пользователя
            user = await self.get_user(user_id)
            if user:
                user.is_premium = True
                user.premium_until = expires_at
            
            session.add(subscription)
            await session.commit()
            await session.refresh(subscription)
            logger.info(f"Created {plan} subscription for user {user_id}")
            return subscription
    
    async def get_user_subscription(self, user_id: int) -> Optional[Subscription]:
        """Получить активную подписку пользователя (асинхронно)"""
        async with session_maker() as session:
            from sqlalchemy import and_
            result = await session.execute(
                select(Subscription)
                .where(and_(
                    Subscription.user_id == user_id,
                    Subscription.status == 'active',
                    Subscription.expires_at > datetime.utcnow()
                ))
                .order_by(Subscription.created_at.desc())
            )
            return result.scalar_one_or_none()
    
    async def check_premium_access(self, user_id: int) -> bool:
        """Проверить есть ли у пользователя премиум доступ (асинхронно)"""
        subscription = await self.get_user_subscription(user_id)
        if subscription:
            return True
        
        # Проверяем поле premium_until у пользователя
        user = await self.get_user(user_id)
        if user and user.premium_until and user.premium_until > datetime.utcnow():
            return True
        
        return False
    
    async def expire_old_subscriptions(self):
        """Отметить просроченные подписки как неактивные (асинхронно)"""
        async with session_maker() as session:
            result = await session.execute(
                select(Subscription)
                .where(Subscription.status == 'active')
                .where(Subscription.expires_at <= datetime.utcnow())
            )
            expired_subscriptions = result.scalars().all()
            
            for subscription in expired_subscriptions:
                subscription.status = 'expired'
                # Обновляем пользователя
                user = await self.get_user(subscription.user_id)
                if user:
                    user.is_premium = False
            
            if expired_subscriptions:
                await session.commit()
                logger.info(f"Expired {len(expired_subscriptions)} subscriptions")
    
    async def get_user_active_subscriptions(self, user_id: int) -> List[Subscription]:
        """Получить все активные подписки пользователя (асинхронно)"""
        async with session_maker() as session:
            from sqlalchemy import and_
            result = await session.execute(
                select(Subscription)
                .where(and_(
                    Subscription.user_id == user_id,
                    Subscription.status == 'active'
                ))
                .order_by(Subscription.created_at.desc())
            )
            return result.scalars().all()
    
    async def cancel_subscription(self, subscription_id: int) -> bool:
        """Отменить подписку (асинхронно)"""
        async with session_maker() as session:
            result = await session.execute(
                select(Subscription).where(Subscription.id == subscription_id)
            )
            subscription = result.scalar_one_or_none()
            
            if subscription:
                subscription.status = 'canceled'
                
                # Проверяем есть ли другие активные подписки
                active_subs = await self.get_user_active_subscriptions(subscription.user_id)
                if not active_subs:
                    user = await self.get_user(subscription.user_id)
                    if user:
                        user.is_premium = False
                
                await session.commit()
                logger.info(f"Cancelled subscription {subscription_id}")
                return True
            
            return False

    # === STATISTICS METHODS ===
    async def get_user_stats(self, user_id: int) -> dict:
        """Получить статистику пользователя (асинхронно)"""
        total_calculations = await self.get_calculations_count(user_id)
        is_premium = await self.check_premium_access(user_id)
        
        calculations = await self.get_user_calculations(user_id, limit=50)
        calc_types = {}
        for calc in calculations:
            calc_types[calc.calc_type] = calc_types.get(calc.calc_type, 0) + 1
        
        # Получаем информацию о подписке
        subscription_info = None
        subscription = await self.get_user_subscription(user_id)
        if subscription:
            subscription_info = {
                'plan': subscription.plan,
                'expires_at': subscription.expires_at.strftime('%d.%m.%Y'),
                'days_remaining': (subscription.expires_at - datetime.utcnow()).days
            }
        
        return {
            'total_calculations': total_calculations,
            'calc_types': calc_types,
            'is_premium': is_premium,
            'subscription': subscription_info
        }
    
    async def get_global_stats(self) -> dict:
        """Получить глобальную статистику (асинхронно)"""
        async with session_maker() as session:
            # Общее количество пользователей
            result = await session.execute(select(User))
            total_users = len(result.scalars().all())
            
            # Премиум пользователи
            result = await session.execute(select(User).where(User.is_premium == True))
            premium_users = len(result.scalars().all())
            
            # Общее количество расчетов
            result = await session.execute(select(Calculation))
            total_calculations = len(result.scalars().all())
            
            # Расчеты по типам
            result = await session.execute(select(Calculation))
            all_calculations = result.scalars().all()
            calc_types = {}
            for calc in all_calculations:
                calc_types[calc.calc_type] = calc_types.get(calc.calc_type, 0) + 1
            
            return {
                'total_users': total_users,
                'premium_users': premium_users,
                'total_calculations': total_calculations,
                'calc_types': calc_types,
                'premium_conversion_rate': round((premium_users / total_users * 100), 2) if total_users > 0 else 0
            }
    
    # === ADMIN METHODS ===
    async def get_recent_users(self, limit: int = 10) -> List[User]:
        """Получить последних пользователей (асинхронно)"""
        async with session_maker() as session:
            result = await session.execute(
                select(User)
                .order_by(User.created_at.desc())
                .limit(limit)
            )
            return result.scalars().all()
    
    async def get_recent_calculations(self, limit: int = 20) -> List[Calculation]:
        """Получить последние расчеты (асинхронно)"""
        async with session_maker() as session:
            result = await session.execute(
                select(Calculation)
                .order_by(Calculation.created_at.desc())
                .limit(limit)
            )
            return result.scalars().all()
    
    async def cleanup_old_data(self, days: int = 30):
        """Очистить старые данные (асинхронно)"""
        async with session_maker() as session:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Удаляем старые расчеты (сохраняем только для активных пользователей)
            result = await session.execute(
                select(Calculation)
                .where(Calculation.created_at < cutoff_date)
            )
            old_calculations = result.scalars().all()
            
            for calculation in old_calculations:
                await session.delete(calculation)
            
            if old_calculations:
                await session.commit()
                logger.info(f"Cleaned up {len(old_calculations)} old calculations")