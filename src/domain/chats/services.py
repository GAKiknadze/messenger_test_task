from typing import Protocol
from uuid import UUID

from .entities import Chat, ChatType
from .repositories import AbstractChatRepository


class AbstractChatService(Protocol):
    async def create(self, chat_type: ChatType, title: str) -> Chat:
        """Создать чат

        Args:
            chat_type (ChatType): Тип чата
            title (str): Название чата

        Returns:
            Chat: Объект чата
        """
        ...

    async def get(self, _id: UUID) -> Chat:
        """Получить чат по его идентификатору

        Args:
            _id (UUID): Идентификатор чата

        Returns:
            Chat: Объект чата

        Raises:
            ObjectNotFoundExc: Чат не найден
        """
        ...

    async def update(
        self,
        _id: UUID,
        title: str | None = None,
    ) -> Chat:
        """_summary_

        Args:
            _id (UUID): Идентификатор чата
            title (str | None, optional): Название чата

        Returns:
            Chat: Объект чата

        Raises:
            ObjectNotFoundExc: Чат не найден
        """
        ...

    async def delete(self, _id: UUID) -> None:
        """Удалить чат

        Args:
            _id (UUID): Идентификатор чата

        Raises:
            ObjectNotFoundExc: Чат не найден
        """
        ...


class ChatService:
    def __init__(self, chat_repository: AbstractChatRepository):
        self.__chat_repo = chat_repository

    async def create(self, chat_type, title):
        return await self.__chat_repo.create(chat_type=chat_type, title=title)

    async def get(self, _id):
        return await self.__chat_repo.get(_id=_id)

    async def update(self, _id, title: str | None = None):
        return await self.__chat_repo.update(_id=_id, title=title)

    async def delete(self, _id):
        return await self.__chat_repo.delete(_id=_id)
