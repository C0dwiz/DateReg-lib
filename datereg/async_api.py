"""
Асинхронный модуль для работы с DateReg API
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

import aiohttp

if TYPE_CHECKING:
    from types import TracebackType

from .cache import TTLCache, make_cache_key
from .exceptions import (
    DateRegAPIError,
    DateRegAuthenticationError,
    DateRegForbiddenError,
    DateRegNotFoundError,
    DateRegPaymentError,
    DateRegServerError,
)
from .models import (
    CreationDateByUsernameResponse,
    CreationDateResponse,
    ResolveUsernameResponse,
)


class AsyncDateRegAPI:
    """
    Асинхронный клиент для работы с DateRegBot API

    Args:
        token: API-ключ для аутентификации
        base_url: Базовый URL API (по умолчанию: https://api.goy.guru/api/v1)
        timeout: Таймаут запросов в секундах (по умолчанию: 30)
        cache: Экземпляр TTLCache для кеширования. Если None, кеширование отключено.
        cache_ttl: Время жизни кеша в секундах (по умолчанию: 3600)
        cache_maxsize: Максимальное количество элементов в кеше (по умолчанию: 128)
        use_models: Использовать dataclass модели вместо словарей (по умолчанию: True)
    """

    BASE_URL = "https://api.goy.guru/api/v1"

    def __init__(
        self,
        token: str,
        base_url: str | None = None,
        timeout: int = 30,
        cache: TTLCache | None = None,
        cache_ttl: int = 3600,
        cache_maxsize: int = 128,
        use_models: bool = True,
    ) -> None:
        if not token:
            raise ValueError("API token cannot be empty")

        self.token = token
        self.base_url = base_url or self.BASE_URL
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.use_models = use_models
        self._session: aiohttp.ClientSession | None = None
        self._own_session = False

        # Настройка кеша
        if cache is not None:
            self.cache = cache
        else:
            self.cache = TTLCache(maxsize=cache_maxsize, ttl=cache_ttl)

    @property
    def session(self) -> aiohttp.ClientSession:
        """Получает или создает сессию aiohttp"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
            self._own_session = True
        return self._session

    async def __aenter__(self) -> AsyncDateRegAPI:
        """Поддержка async context manager"""
        if self._session is None:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
            self._own_session = True
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Закрытие сессии при выходе из async context manager"""
        await self.close()

    async def close(self) -> None:
        """Закрывает сессию aiohttp"""
        if self._session and not self._session.closed and self._own_session:
            await self._session.close()
            self._session = None

    async def _make_request(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        use_cache: bool = True,
    ) -> dict[str, Any]:
        """
        Выполняет асинхронный HTTP запрос к API с поддержкой кеширования

        Args:
            endpoint: Endpoint API (например, /users/getCreationDateSmart)
            params: Параметры запроса
            use_cache: Использовать кеш (по умолчанию: True)

        Returns:
            Словарь с данными ответа

        Raises:
            DateRegAPIError: При ошибках API
        """
        request_params = params.copy() if params else {}

        # Проверяем кеш
        if use_cache:
            cache_key = make_cache_key(endpoint, request_params)
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                return cached_result

        url = f"{self.base_url}{endpoint}"
        request_params["token"] = self.token

        try:
            async with self.session.get(url, params=request_params) as response:
                await self._handle_response(response)
                result = await response.json()

                # Сохраняем в кеш
                if use_cache:
                    cache_key = make_cache_key(endpoint, params or {})
                    self.cache.set(cache_key, result)

                return result
        except aiohttp.ClientError as e:
            raise DateRegAPIError(f"Ошибка при выполнении запроса: {e}") from e
        except asyncio.TimeoutError as e:
            raise DateRegAPIError(f"Превышено время ожидания запроса: {e}") from e

    async def _handle_response(self, response: aiohttp.ClientResponse) -> None:
        """
        Обрабатывает HTTP ответ и выбрасывает соответствующие исключения

        Args:
            response: Объект ответа aiohttp

        Raises:
            DateRegAPIError: При ошибках API
        """
        status_code = response.status

        if status_code == 200:
            return

        # Извлекаем детали ошибки
        try:
            error_data = await response.json()
            detail = error_data.get("detail", "Unknown error")
        except (ValueError, aiohttp.ContentTypeError):
            detail = await response.text() or "Unknown error"

        # Маппинг статус-кодов на исключения
        error_message_map: dict[int, tuple[type[DateRegAPIError], str]] = {
            400: (DateRegAPIError, "Ошибка в параметрах запроса"),
            401: (DateRegAuthenticationError, "Недействительный API-ключ"),
            402: (DateRegPaymentError, "Недостаточно средств на балансе"),
            403: (DateRegForbiddenError, "API-ключ заблокирован или метод запрещен"),
            404: (DateRegNotFoundError, "Endpoint не найден"),
        }

        if status_code in error_message_map:
            error_class, error_msg = error_message_map[status_code]
            raise error_class(
                f"{error_msg}: {detail}", status_code=status_code, detail=detail
            )
        elif status_code >= 500:
            raise DateRegServerError(
                f"Внутренняя ошибка сервера: {detail}",
                status_code=status_code,
                detail=detail,
            )
        else:
            raise DateRegAPIError(
                f"Неожиданная ошибка (HTTP {status_code}): {detail}",
                status_code=status_code,
                detail=detail,
            )

    async def get_creation_date_fast(
        self,
        user_id: int,
        use_cache: bool = True,
    ) -> CreationDateResponse | dict[str, Any]:
        """
        Определяет приблизительную дату регистрации пользователя Telegram
        с точностью до месяца. Это самый быстрый, но наименее точный метод.

        Args:
            user_id: ID пользователя Telegram
            use_cache: Использовать кеш (по умолчанию: True)

        Returns:
            CreationDateResponse если use_models=True, иначе dict с данными

        Raises:
            ValueError: Если user_id некорректен
            DateRegAPIError: При ошибках API
        """
        if user_id <= 0:
            raise ValueError("user_id must be a positive integer")

        result = await self._make_request(
            "/users/getCreationDateFast",
            params={"user_id": user_id},
            use_cache=use_cache,
        )

        return CreationDateResponse.from_dict(result) if self.use_models else result

    async def get_creation_date_smart(
        self,
        user_id: int,
        use_cache: bool = True,
    ) -> CreationDateResponse | dict[str, Any]:
        """
        Определяет дату регистрации пользователя Telegram с точностью до месяца.
        Этот метод использует 12 алгоритмов, включая собственную нейросеть.

        Args:
            user_id: ID пользователя Telegram
            use_cache: Использовать кеш (по умолчанию: True)

        Returns:
            CreationDateResponse если use_models=True, иначе dict с данными

        Raises:
            ValueError: Если user_id некорректен
            DateRegAPIError: При ошибках API
        """
        if user_id <= 0:
            raise ValueError("user_id must be a positive integer")

        result = await self._make_request(
            "/users/getCreationDateSmart",
            params={"user_id": user_id},
            use_cache=use_cache,
        )

        return CreationDateResponse.from_dict(result) if self.use_models else result

    async def get_creation_date_by_username(
        self,
        username: str,
        use_cache: bool = True,
    ) -> CreationDateByUsernameResponse | dict[str, Any]:
        """
        Определяет дату регистрации пользователя Telegram по его username.
        Метод сначала преобразует username в ID, а затем применяет алгоритм
        getCreationDateSmart.

        Args:
            username: Имя пользователя Telegram (без символа @)
            use_cache: Использовать кеш (по умолчанию: True)

        Returns:
            CreationDateByUsernameResponse если use_models=True, иначе dict с данными

        Raises:
            ValueError: Если username пустой
            DateRegAPIError: При ошибках API
        """
        if not username:
            raise ValueError("Username cannot be empty")

        # Убираем @ если он есть
        username = username.lstrip("@")

        result = await self._make_request(
            "/users/getCreationDateByUsername",
            params={"username": username},
            use_cache=use_cache,
        )

        return (
            CreationDateByUsernameResponse.from_dict(result)
            if self.use_models
            else result
        )

    async def resolve_username(
        self,
        username: str,
        use_cache: bool = True,
    ) -> ResolveUsernameResponse | dict[str, Any]:
        """
        Преобразует имя пользователя Telegram (username) в ID пользователя
        и возвращает полную информацию о пользователе.

        Args:
            username: Имя пользователя Telegram (без символа @)
            use_cache: Использовать кеш (по умолчанию: True)

        Returns:
            ResolveUsernameResponse если use_models=True, иначе dict с данными

        Raises:
            ValueError: Если username пустой
            DateRegAPIError: При ошибках API
        """
        if not username:
            raise ValueError("Username cannot be empty")

        # Убираем @ если он есть
        username = username.lstrip("@")

        result = await self._make_request(
            "/users/resolveUsername",
            params={"username": username},
            use_cache=use_cache,
        )

        return ResolveUsernameResponse.from_dict(result) if self.use_models else result

    def clear_cache(self) -> None:
        """Очищает весь кеш"""
        self.cache.clear()

    def get_cache_size(self) -> int:
        """Возвращает количество элементов в кеше"""
        return len(self.cache)
