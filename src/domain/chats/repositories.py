from typing import Protocol
from uuid import UUID

from ...common.repositories import AbstractDelete, AbstractGet, AbstractUpdate
from .entities import Chat, ChatType


class AbstractChatRepository(
    AbstractGet[UUID, Chat],
    AbstractUpdate[UUID, Chat],
    AbstractDelete[UUID, Chat],
    Protocol,
):
    async def create(self, chat_type: ChatType, title: str) -> Chat:
        """Создать чат

        Args:
            chat_type (ChatType): Тип чата
            title (str): Название чата

        Returns:
            Chat: Объект чата
        """
        ...
