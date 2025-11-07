"""
Dataclass модели для ответов API
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class CreationDateResponse:
    """Модель ответа для методов определения даты регистрации"""

    user_id: int
    creation_date: str
    accuracy_text: str
    accuracy_percent: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CreationDateResponse:
        """Создает объект из словаря ответа API"""
        return cls(
            user_id=int(data["user_id"]),
            creation_date=str(data["creation_date"]),
            accuracy_text=str(data["accuracy_text"]),
            accuracy_percent=int(data["accuracy_percent"]),
        )

    def __str__(self) -> str:
        return (
            f"CreationDateResponse(user_id={self.user_id}, "
            f"creation_date={self.creation_date}, "
            f"accuracy={self.accuracy_percent}%)"
        )


@dataclass(frozen=True, slots=True)
class CreationDateByUsernameResponse:
    """Модель ответа для метода определения даты регистрации по username"""

    username: str
    user_id: int
    creation_date: str
    accuracy_text: str
    accuracy_percent: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CreationDateByUsernameResponse:
        """Создает объект из словаря ответа API"""
        return cls(
            username=str(data["username"]),
            user_id=int(data["user_id"]),
            creation_date=str(data["creation_date"]),
            accuracy_text=str(data["accuracy_text"]),
            accuracy_percent=int(data["accuracy_percent"]),
        )

    def __str__(self) -> str:
        return (
            f"CreationDateByUsernameResponse(username={self.username}, "
            f"user_id={self.user_id}, creation_date={self.creation_date}, "
            f"accuracy={self.accuracy_percent}%)"
        )


@dataclass(frozen=True, slots=True)
class UsernameInfo:
    """Информация о username пользователя"""

    username: str
    editable: bool
    active: bool

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UsernameInfo:
        """Создает объект из словаря"""
        return cls(
            username=str(data["username"]),
            editable=bool(data.get("editable", False)),
            active=bool(data.get("active", True)),
        )


@dataclass(frozen=True, slots=True)
class UserPhoto:
    """Информация о фото пользователя"""

    photo_id: int
    dc_id: int
    has_video: bool
    personal: bool
    stripped_thumb: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UserPhoto:
        """Создает объект из словаря"""
        return cls(
            photo_id=int(data["photo_id"]),
            dc_id=int(data["dc_id"]),
            has_video=bool(data.get("has_video", False)),
            personal=bool(data.get("personal", False)),
            stripped_thumb=data.get("stripped_thumb"),
        )


@dataclass(frozen=True, slots=True)
class ResolveUsernameResponse:
    """Модель ответа для метода resolveUsername"""

    id: int
    first_name: str | None
    last_name: str | None
    username: str | None
    phone: str | None
    premium: bool
    verified: bool
    bot: bool
    deleted: bool
    scam: bool
    fake: bool
    access_hash: int | None = None
    photo: UserPhoto | None = None
    usernames: list[UsernameInfo] = field(default_factory=list) # type: ignore
    raw_data: dict[str, Any] = field(default_factory=dict, repr=False) # type: ignore

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ResolveUsernameResponse:
        """Создает объект из словаря ответа API"""
        photo = None
        if "photo" in data and data["photo"]:
            photo = UserPhoto.from_dict(data["photo"])

        usernames = []
        if "usernames" in data and data["usernames"]:
            usernames = [UsernameInfo.from_dict(u) for u in data["usernames"]]

        return cls(
            id=int(data["id"]),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            username=data.get("username"),
            phone=data.get("phone"),
            premium=bool(data.get("premium", False)),
            verified=bool(data.get("verified", False)),
            bot=bool(data.get("bot", False)),
            deleted=bool(data.get("deleted", False)),
            scam=bool(data.get("scam", False)),
            fake=bool(data.get("fake", False)),
            access_hash=data.get("access_hash"),
            photo=photo,
            usernames=usernames,
            raw_data=data,
        )

    def __str__(self) -> str:
        name = self.first_name or ""
        if self.last_name:
            name = f"{name} {self.last_name}".strip()
        return (
            f"ResolveUsernameResponse(id={self.id}, "
            f"name={name or 'N/A'}, username={self.username or 'N/A'}, "
            f"premium={self.premium})"
        )
