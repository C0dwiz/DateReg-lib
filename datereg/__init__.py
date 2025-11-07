"""
DateReg API Library - Python библиотека для работы с DateRegBot API
"""

from .api import DateRegAPI
from .async_api import AsyncDateRegAPI
from .cache import TTLCache
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
    UsernameInfo,
    UserPhoto,
)

__version__ = "1.0.0"
__all__ = [
    "DateRegAPI",
    "AsyncDateRegAPI",
    "DateRegAPIError",
    "DateRegAuthenticationError",
    "DateRegPaymentError",
    "DateRegForbiddenError",
    "DateRegNotFoundError",
    "DateRegServerError",
    "CreationDateResponse",
    "CreationDateByUsernameResponse",
    "ResolveUsernameResponse",
    "UsernameInfo",
    "UserPhoto",
    "TTLCache",
]
