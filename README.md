# DateReg API Library

Python библиотека для работы с [DateRegBot API](https://docs.goy.guru/api) - получение даты регистрации аккаунтов Telegram, ID пользователей по их имени и другие данные.

## Требования

- Python 3.9+

## Установка

```bash
pip install git+https://github.com/C0dwiz/DateReg-lib/archive/main.zip --force-reinstall
```

## Быстрый старт

```python
from datereg import DateRegAPI

# Инициализация клиента
api = DateRegAPI(token="YOUR_API_TOKEN")

# Получить дату регистрации по ID (быстрый метод)
result = api.get_creation_date_fast(user_id=6362784873)
print(f"Дата регистрации: {result['creation_date']}")
print(f"Точность: {result['accuracy_text']}")

# Получить дату регистрации по ID (умный метод)
result = api.get_creation_date_smart(user_id=7308887716)
print(f"Дата регистрации: {result['creation_date']}")
print(f"Точность: {result['accuracy_percent']}%")

# Получить дату регистрации по username
result = api.get_creation_date_by_username(username="filimono")
print(f"Пользователь: {result['username']} (ID: {result['user_id']})")
print(f"Дата регистрации: {result['creation_date']}")

# Преобразовать username в ID
user_info = api.resolve_username(username="pvxdev")
print(f"ID: {user_info['id']}")
print(f"Имя: {user_info['first_name']}")
print(f"Премиум: {user_info['premium']}")
```

## Методы API

### `get_creation_date_fast(user_id: int)`

Определяет приблизительную дату регистрации пользователя Telegram с точностью до месяца. Это самый быстрый, но наименее точный метод.

**Параметры:**
- `user_id` (int): ID пользователя Telegram

**Возвращает:**
```python
{
    "user_id": 6362784873,
    "creation_date": "1.2024",
    "accuracy_text": "точная запись (100%)",
    "accuracy_percent": 100
}
```

**Стоимость:** $0.0005 за запрос

### `get_creation_date_smart(user_id: int)`

Определяет дату регистрации пользователя Telegram с точностью до месяца. Этот метод использует 12 алгоритмов, включая собственную нейросеть.

**Параметры:**
- `user_id` (int): ID пользователя Telegram

**Возвращает:**
```python
{
    "user_id": 7308887716,
    "creation_date": "10.2024",
    "accuracy_text": "высокая (87%)",
    "accuracy_percent": 87
}
```

**Стоимость:** $0.001 за запрос

### `get_creation_date_by_username(username: str)`

Определяет дату регистрации пользователя Telegram по его username. Метод сначала преобразует username в ID, а затем применяет алгоритм getCreationDateSmart.

**Параметры:**
- `username` (str): Имя пользователя Telegram (можно с @ или без)

**Возвращает:**
```python
{
    "username": "filimono",
    "user_id": 678158951,
    "creation_date": "12.2018",
    "accuracy_text": "высокая (89%)",
    "accuracy_percent": 89
}
```

**Стоимость:** $0.003 за запрос

### `resolve_username(username: str)`

Преобразует имя пользователя Telegram (username) в ID пользователя и возвращает полную информацию о пользователе.

**Параметры:**
- `username` (str): Имя пользователя Telegram (можно с @ или без)

**Возвращает:**
```python
{
    "id": 6362784873,
    "first_name": "Pavel",
    "last_name": null,
    "username": null,
    "phone": null,
    "premium": true,
    # ... и другие поля
}
```

**Стоимость:** $0.0025 за запрос

## Обработка ошибок

Библиотека предоставляет специальные исключения для различных типов ошибок:

```python
from datereg import (
    DateRegAPI,
    DateRegAuthenticationError,
    DateRegPaymentError,
    DateRegForbiddenError,
    DateRegNotFoundError,
    DateRegServerError,
    DateRegAPIError,
)

api = DateRegAPI(token="YOUR_API_TOKEN")

try:
    result = api.get_creation_date_smart(user_id=123456789)
except DateRegAuthenticationError:
    print("Недействительный API-ключ")
except DateRegPaymentError:
    print("Недостаточно средств на балансе")
except DateRegForbiddenError:
    print("API-ключ заблокирован")
except DateRegNotFoundError:
    print("Endpoint не найден")
except DateRegServerError:
    print("Ошибка сервера")
except DateRegAPIError as e:
    print(f"Ошибка API: {e}")
```

## Получение API-ключа

1. Откройте бота [@dateregbot](https://t.me/dateregbot) в Telegram
2. Отправьте команду `/api` или нажмите на гиперссылку API в главном меню
3. Скопируйте API-ключ

## Тарифы

| Метод | Стоимость за запрос | Стоимость за 1000 запросов |
|-------|---------------------|----------------------------|
| `getCreationDateFast` | $0.0005 | $0.5 |
| `getCreationDateSmart` | $0.001 | $1.0 |
| `getCreationDateByUsername` | $0.003 | $3.0 |
| `resolveUsername` | $0.0025 | $2.5 |

## Дополнительные параметры

При инициализации клиента можно указать дополнительные параметры:

```python
api = DateRegAPI(
    token="YOUR_API_TOKEN",
    base_url="https://api.goy.guru/api/v1",  # По умолчанию
    timeout=30  # Таймаут запросов в секундах
)
```

## Использование context manager

Библиотека поддерживает использование в качестве context manager для автоматического закрытия сессии:

```python
with DateRegAPI(token="YOUR_API_TOKEN") as api:
    result = api.get_creation_date_smart(user_id=123456789)
    print(result['creation_date'])
# Сессия автоматически закрыта
```

## Валидация параметров

Библиотека автоматически проверяет корректность входных параметров:

```python
api = DateRegAPI(token="YOUR_API_TOKEN")

# Вызовет ValueError если user_id <= 0
api.get_creation_date_smart(user_id=-1)

# Вызовет ValueError если username пустой
api.resolve_username(username="")
```

## Лицензия

[MIT](LICENSE)

## Поддержка

Если у вас возникли вопросы или проблемы:

- 📖 [Документация API](https://docs.goy.guru/api)
- 💬 Telegram: [@gitapps](https://t.me/gitapps)
- 🤖 Бот: [@dateregbot](https://t.me/dateregbot)

