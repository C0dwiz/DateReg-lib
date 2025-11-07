"""
Пример использования асинхронного DateReg API Library
"""

import asyncio

from datereg import (
    AsyncDateRegAPI,
    DateRegAPIError,
)

# Замените на ваш API-ключ
API_TOKEN = "YOUR_API_TOKEN"


async def main():
    # Инициализация асинхронного клиента
    async with AsyncDateRegAPI(token=API_TOKEN) as api:
        print("=== Примеры использования AsyncDateReg API ===\n")

        # Пример 1: Быстрый метод определения даты регистрации
        print("1. Быстрый метод (getCreationDateFast):")
        try:
            result = await api.get_creation_date_fast(user_id=6362784873)
            print(f"   ID пользователя: {result.user_id}")
            print(f"   Дата регистрации: {result.creation_date}")
            print(f"   Точность: {result.accuracy_text} ({result.accuracy_percent}%)")
        except DateRegAPIError as e:
            print(f"   Ошибка: {e}")
        print()

        # Пример 2: Умный метод определения даты регистрации
        print("2. Умный метод (getCreationDateSmart):")
        try:
            result = await api.get_creation_date_smart(user_id=7308887716)
            print(f"   ID пользователя: {result.user_id}")
            print(f"   Дата регистрации: {result.creation_date}")
            print(f"   Точность: {result.accuracy_text} ({result.accuracy_percent}%)")
        except DateRegAPIError as e:
            print(f"   Ошибка: {e}")
        print()

        # Пример 3: Определение даты регистрации по username
        print("3. Определение даты по username (getCreationDateByUsername):")
        try:
            result = await api.get_creation_date_by_username(username="filimono")
            print(f"   Username: {result.username}")
            print(f"   ID пользователя: {result.user_id}")
            print(f"   Дата регистрации: {result.creation_date}")
            print(f"   Точность: {result.accuracy_text} ({result.accuracy_percent}%)")
        except DateRegAPIError as e:
            print(f"   Ошибка: {e}")
        print()

        # Пример 4: Преобразование username в ID
        print("4. Преобразование username в ID (resolveUsername):")
        try:
            user_info = await api.resolve_username(username="pvxdev")
            print(f"   ID: {user_info.id}")
            print(f"   Имя: {user_info.first_name or 'N/A'}")
            print(f"   Фамилия: {user_info.last_name or 'N/A'}")
            print(f"   Премиум: {user_info.premium}")
            print(f"   Username: {user_info.username or 'N/A'}")
            if user_info.usernames:
                print(f"   Все usernames: {[u.username for u in user_info.usernames]}")
        except DateRegAPIError as e:
            print(f"   Ошибка: {e}")
        print()

        # Пример 5: Параллельные запросы
        print("5. Параллельные запросы:")
        try:
            user_ids = [6362784873, 7308887716, 678158951]
            tasks = [api.get_creation_date_smart(user_id=uid) for uid in user_ids]
            results = await asyncio.gather(*tasks)
            for result in results:
                print(
                    f"   User {result.user_id}: {result.creation_date} ({result.accuracy_percent}%)"
                )
        except DateRegAPIError as e:
            print(f"   Ошибка: {e}")
        print()

        # Пример 6: Кеширование
        print("6. Пример кеширования:")
        import time

        start = time.time()
        result1 = await api.get_creation_date_smart(user_id=6362784873, use_cache=True)
        time1 = time.time() - start
        print(f"   Первый запрос: {time1:.3f}s")

        start = time.time()
        result2 = await api.get_creation_date_smart(user_id=6362784873, use_cache=True)
        time2 = time.time() - start
        print(f"   Второй запрос (из кеша): {time2:.3f}s")
        print(f"   Ускорение: {time1 / time2:.1f}x")
        print(f"   Размер кеша: {api.get_cache_size()}")


if __name__ == "__main__":
    asyncio.run(main())
