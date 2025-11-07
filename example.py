"""
Пример использования DateReg API Library
"""

import time

from datereg import (
    DateRegAPI,
    DateRegAPIError,
    DateRegAuthenticationError,
    DateRegPaymentError,
)

# Замените на ваш API-ключ
API_TOKEN = "YOUR_API_TOKEN"


def main():
    # Инициализация клиента с кешированием
    api = DateRegAPI(
        token=API_TOKEN,
        cache_ttl=3600,  # Кеш на 1 час
        cache_maxsize=256,  # Максимум 256 элементов
        use_models=True,  # Использовать dataclass модели
    )

    print("=== Примеры использования DateReg API ===\n")

    # Пример 1: Быстрый метод определения даты регистрации
    print("1. Быстрый метод (getCreationDateFast):")
    try:
        result = api.get_creation_date_fast(user_id=6362784873)
        print(f"   ID пользователя: {result.user_id}")
        print(f"   Дата регистрации: {result.creation_date}")
        print(f"   Точность: {result.accuracy_text} ({result.accuracy_percent}%)")
    except DateRegAPIError as e:
        print(f"   Ошибка: {e}")
    print()

    # Пример 2: Умный метод определения даты регистрации
    print("2. Умный метод (getCreationDateSmart):")
    try:
        result = api.get_creation_date_smart(user_id=7308887716)
        print(f"   ID пользователя: {result.user_id}")
        print(f"   Дата регистрации: {result.creation_date}")
        print(f"   Точность: {result.accuracy_text} ({result.accuracy_percent}%)")
    except DateRegAPIError as e:
        print(f"   Ошибка: {e}")
    print()

    # Пример 3: Определение даты регистрации по username
    print("3. Определение даты по username (getCreationDateByUsername):")
    try:
        result = api.get_creation_date_by_username(username="filimono")
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
        user_info = api.resolve_username(username="pvxdev")
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

    # Пример 5: Использование context manager
    print("5. Использование context manager:")
    try:
        with DateRegAPI(token=API_TOKEN) as api_ctx:
            result = api_ctx.get_creation_date_fast(user_id=6362784873)
            print(f"   Дата регистрации: {result.creation_date}")
            print("   ✓ Сессия автоматически закрыта после выхода из with")
    except DateRegAPIError as e:
        print(f"   Ошибка: {e}")
    print()

    # Пример 6: Кеширование
    print("6. Пример кеширования:")
    try:
        start = time.time()
        _ = api.get_creation_date_smart(user_id=6362784873, use_cache=True)
        time1 = time.time() - start
        print(f"   Первый запрос: {time1:.3f}s")

        start = time.time()
        _ = api.get_creation_date_smart(user_id=6362784873, use_cache=True)
        time2 = time.time() - start
        print(f"   Второй запрос (из кеша): {time2:.3f}s")
        if time2 > 0:
            print(f"   Ускорение: {time1 / time2:.1f}x")
        print(f"   Размер кеша: {api.get_cache_size()}")
    except DateRegAPIError as e:
        print(f"   Ошибка: {e}")
    print()

    # Пример 7: Использование без кеша
    print("7. Запрос без кеша:")
    try:
        result = api.get_creation_date_smart(user_id=6362784873, use_cache=False)
        print(f"   Дата регистрации: {result.creation_date}")
    except DateRegAPIError as e:
        print(f"   Ошибка: {e}")
    print()

    # Пример 8: Обработка ошибок
    print("8. Пример обработки различных ошибок:")
    try:
        # Попытка с неверным API-ключом
        api_invalid = DateRegAPI(token="invalid_token")
        api_invalid.get_creation_date_smart(user_id=123456789)
    except DateRegAuthenticationError:
        print("   ✓ Поймана ошибка аутентификации")
    except DateRegPaymentError:
        print("   ✓ Поймана ошибка недостатка средств")
    except DateRegAPIError as e:
        print(f"   ✓ Поймана общая ошибка API: {e}")
    print()

    # Пример 9: Использование словарей вместо моделей
    print("9. Использование словарей вместо моделей:")
    try:
        api_dict = DateRegAPI(token=API_TOKEN, use_models=False)
        result = api_dict.get_creation_date_smart(user_id=6362784873)
        print(f"   Тип результата: {type(result)}")
        print(f"   Дата регистрации: {result['creation_date']}")
    except DateRegAPIError as e:
        print(f"   Ошибка: {e}")


if __name__ == "__main__":
    main()
