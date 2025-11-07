"""
Исключения для DateReg API
"""

from __future__ import annotations


class DateRegAPIError(Exception):
    """Базовое исключение для всех ошибок API"""

    def __init__(
        self, message: str, status_code: int | None = None, detail: str | None = None
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"status_code={self.status_code}, "
            f"detail={self.detail!r})"
        )


class DateRegAuthenticationError(DateRegAPIError):
    """Ошибка аутентификации (401) - недействительный API-ключ"""

    pass


class DateRegPaymentError(DateRegAPIError):
    """Ошибка оплаты (402) - недостаточно средств на балансе"""

    pass


class DateRegForbiddenError(DateRegAPIError):
    """Ошибка доступа (403) - API-ключ заблокирован или метод запрещен"""

    pass


class DateRegNotFoundError(DateRegAPIError):
    """Ошибка (404) - endpoint не найден"""

    pass


class DateRegServerError(DateRegAPIError):
    """Ошибка сервера (500) - внутренняя ошибка сервера"""

    pass
