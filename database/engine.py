# database/engine.py
import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from database.models import Base

# Асинхронный SQLite
DB_URL = os.getenv('DB_URL', 'sqlite+aiosqlite:///tax_bot.db')

engine = create_async_engine(DB_URL, echo=True)
session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def create_db():
    """Создать все таблицы в базе"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ База данных создана!")

async def drop_db():
    """Удалить все таблицы из базы"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("🗑️ База данных удалена!")