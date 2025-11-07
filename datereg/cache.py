"""
Система кеширования для DateReg API
"""

from __future__ import annotations

import hashlib
import json
import time
from collections import OrderedDict
from functools import wraps
from typing import Any, Callable, ParamSpec, TypeVar

T = TypeVar("T")
P = ParamSpec("P")


class TTLCache:
    """
    Кеш с временем жизни (TTL - Time To Live)

    Args:
        maxsize: Максимальное количество элементов в кеше
        ttl: Время жизни элемента в секундах
    """

    def __init__(self, maxsize: int = 128, ttl: int = 3600) -> None:
        self.maxsize = maxsize
        self.ttl = ttl
        self._cache: OrderedDict[str, tuple[Any, float]] = OrderedDict()

    def _is_expired(self, timestamp: float) -> bool:
        """Проверяет, истекло ли время жизни элемента"""
        return time.time() - timestamp > self.ttl

    def _cleanup_expired(self) -> None:
        """Удаляет истекшие элементы из кеша"""
        current_time = time.time()
        expired_keys = [
            key
            for key, (_, timestamp) in self._cache.items()
            if current_time - timestamp > self.ttl
        ]
        for key in expired_keys:
            del self._cache[key]

    def get(self, key: str) -> Any | None:
        """Получает значение из кеша"""
        if key not in self._cache:
            return None

        value, timestamp = self._cache[key]

        if self._is_expired(timestamp):
            del self._cache[key]
            return None

        # Перемещаем в конец (LRU)
        self._cache.move_to_end(key)
        return value

    def set(self, key: str, value: Any) -> None:
        """Сохраняет значение в кеш"""

        self._cleanup_expired()

        if len(self._cache) >= self.maxsize and key not in self._cache:
            self._cache.popitem(last=False)

        self._cache[key] = (value, time.time())
        self._cache.move_to_end(key)

    def clear(self) -> None:
        """Очищает весь кеш"""
        self._cache.clear()

    def __len__(self) -> int:
        """Возвращает количество элементов в кеше"""
        self._cleanup_expired()
        return len(self._cache)

    def __contains__(self, key: str) -> bool:
        """Проверяет наличие ключа в кеше"""
        return self.get(key) is not None


def make_cache_key(endpoint: str, params: dict[str, Any]) -> str:
    """
    Создает ключ кеша на основе endpoint и параметров

    Args:
        endpoint: Endpoint API
        params: Параметры запроса (без token)

    Returns:
        Хеш-ключ для кеша
    """

    cache_params = {k: v for k, v in params.items() if k != "token"}
    cache_data = json.dumps(
        {"endpoint": endpoint, "params": cache_params}, sort_keys=True
    )
    return hashlib.sha256(cache_data.encode()).hexdigest()


def cached(cache: TTLCache | None = None) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Декоратор для кеширования результатов функций

    Args:
        cache: Экземпляр TTLCache. Если None, кеширование отключено.

    Returns:
        Декорированная функция
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        if cache is None:
            return func

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            if len(args) >= 3:
                endpoint = str(args[1])
                params = args[2] if len(args) > 2 else {} # type: ignore
                cache_key = make_cache_key(endpoint, params) # type: ignore

                cached_result = cache.get(cache_key) # type: ignore
                if cached_result is not None:
                    return cached_result

                result = func(*args, **kwargs)
                cache.set(cache_key, result) # type: ignore
                return result

            return func(*args, **kwargs)

        return wrapper

    return decorator
