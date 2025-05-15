from typing import Protocol
from uuid import UUID

from .entities import User
from .repositories import AbstractUserRepository


class AbstractUserService(Protocol):
    async def create(self, name: str, email: str, hashed_password: str) -> User:
        """Создать пользователя

        Args:
            name (str): Имя
            email (str): Электронный адрес
            hashed_password (str): Хэш пароля

        Returns:
            User: Объект пользователя

        Raises:
            AlreadyExistsExc: Пользователь с таким EMail уже существует
        """
        ...

    async def get(self, _id: UUID) -> User:
        """Получить пользователя по его идентификатору

        Args:
            _id (UUID): Идентификатор пользователя

        Returns:
            User: Объект пользователя

        Raises:
            ObjectNotFoundExc: Пользователь не найден
        """
        ...

    async def get_by_email(self, email: str) -> User:
        """Получить пользователя по его EMail

        Args:
            email (str): Электронный адрес

        Returns:
            User: Объект пользователя

        Raises:
            ObjectNotFoundExc: Пользователь не найден
        """
        ...

    async def update(
        self,
        _id: UUID,
        name: str | None = None,
        email: str | None = None,
        hashed_password: str | None = None,
    ) -> User:
        """Обновить данные пользователя

        Args:
            _id (UUID): Идентификатор пользователя
            name (str | None, optional): Имя
            email (str | None, optional): Электронный адрес
            hashed_password (str | None, optional): Хэш пароля

        Returns:
            User: Объект пользователя

        Raises:
            ObjectNotFoundExc: Пользователь не найден
            AlreadyExistsExc: Пользователь с таким EMail уже существует
        """
        ...

    async def delete(self, _id: UUID) -> None:
        """Удалить пользователя

        Args:
            _id (UUID): Идентификатор пользователя

        Raises:
            ObjectNotFoundExc: Пользователь не найден
        """
        ...


class UserService:
    def __init__(self, user_repository: AbstractUserRepository):
        self.__user_repo = user_repository

    async def create(self, name: str, email: str, hashed_password: str) -> User:
        return await self.__user_repo.create(
            name=name, email=email, hashed_password=hashed_password
        )

    async def get(self, _id: UUID) -> User:
        return await self.__user_repo.get(_id=_id)

    async def get_by_email(self, email: str) -> User:
        return await self.__user_repo.get_by_email(email=email)

    async def update(
        self,
        _id: UUID,
        name: str | None = None,
        email: str | None = None,
        hashed_password: str | None = None,
    ) -> User:
        attrs = dict()
        if name is not None:
            attrs.update({"name": name})
        if email is not None:
            attrs.update({"email": email})
        if hashed_password is not None:
            attrs.update({"hashed_password": hashed_password})

        return await self.__user_repo.update(_id, **attrs)

    async def delete(self, _id: UUID) -> None:
        return await self.__user_repo.delete(_id=_id)
