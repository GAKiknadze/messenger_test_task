from typing import Protocol
from uuid import UUID

from ...common.repositories import AbstractDelete, AbstractGet, AbstractUpdate
from .entities import User


class AbstractUserRepository(
    AbstractGet[UUID, User],
    AbstractUpdate[UUID, User],
    AbstractDelete[UUID, User],
    Protocol,
):
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
