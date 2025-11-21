# test_db.py
import asyncio
import sys
import os

# Добавляем текущую директорию в путь для импортов
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.engine import create_db, drop_db
from services.database import DatabaseService

async def test_database():
    print("🧪 Начинаем тест базы данных...")
    
    try:
        # 1. Создаем базу
        print("1. Создаем базу данных...")
        await create_db()
        
        # 2. Тестируем сервис
        print("2. Тестируем DatabaseService...")
        db = DatabaseService()
        
        # 3. Создаем пользователя
        print("3. Создаем тестового пользователя...")
        user = await db.get_or_create_user(
            user_id=12345,
            username="test_user",
            first_name="Тест",
            last_name="Пользователь"
        )
        print(f"   ✅ Пользователь создан: ID {user.user_id}")
        
        # 4. Сохраняем расчет
        print("4. Сохраняем тестовый расчет...")
        calculation = await db.save_calculation(
            user_id=12345,
            calc_type="ndfl",
            income=100000,
            expenses=0,
            result_data={
                "tax": 13000,
                "net_income": 87000,
                "calculation": "НДФЛ 13%"
            }
        )
        print(f"   ✅ Расчет сохранен: {calculation.calc_type}")
        
        # 5. Получаем историю
        print("5. Получаем историю расчетов...")
        calculations = await db.get_user_calculations(12345)
        print(f"   ✅ Найдено расчетов: {len(calculations)}")
        
        # 6. Получаем статистику
        print("6. Получаем статистику...")
        stats = await db.get_user_stats(12345)
        print(f"   ✅ Статистика: {stats}")
        
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_database())