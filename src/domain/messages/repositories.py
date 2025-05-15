from typing import Protocol, Sequence
from uuid import UUID

from ...common.repositories import AbstractGet
from .entities import Message, SourceType


class AbstractMessageRepository(AbstractGet[UUID, Message], Protocol):
    async def create(
        self,
        source_id: UUID,
        source_type: SourceType,
        sender_id: UUID,
        text_content: str,
    ) -> Message:
        """Создать сообщение

        Args:
            source_id (UUID): Идентификатор ресурса
            source_type (SourceType): Тип ресурса
            sender_id (UUID): Идентификатор отправителя
            text_content (str): Текстовое сообщение

        Returns:
            Message: Объект сообщения
        """
        ...

    async def get_list(
        self, source_id: UUID, source_type: SourceType, offset: int = 0, limit: int = 50
    ) -> Sequence[Message]:
        """Получить список сообщений

        Args:
            source_id (UUID): Идентификатор ресурса
            source_type (SourceType): Тип ресурса
            offset (int, optional): Смещение. По умолчанию 0.
            limit (int, optional): Лимит. По умолчанию 50.

        Returns:
            Sequence[Message]: Список сообщений
        """
        ...
