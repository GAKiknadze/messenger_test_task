from typing import Protocol, Sequence
from uuid import UUID

from .entities import Message, SourceType
from .repositories import AbstractMessageRepository


class AbstractMessageService(Protocol):
    async def send(
        self,
        source_id: UUID,
        source_type: SourceType,
        sender_id: UUID,
        text_content: str,
    ) -> Message:
        """Отправить сообщение

        Args:
            source_id (UUID): Идентификатор ресурса
            source_type (SourceType): Тип ресурса
            sender_id (UUID): Идентификатор отправителя
            text_content (str): Текстовое сообщение

        Returns:
            Message: Объект сообщения
        """
        ...

    async def get(self, _id: UUID) -> Message:
        """Получить сообщение

        Args:
            _id (UUID): Идентификатор сообщения

        Returns:
            Message: Объект сообщения

        Raises:
            ObjectNotFoundExc: Сообщение не найдено
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


class MessageService:
    def __init__(self, message_repository: AbstractMessageRepository):
        self.__message_repo = message_repository

    async def send(
        self,
        source_id: UUID,
        source_type: SourceType,
        sender_id: UUID,
        text_content: str,
    ) -> Message:
        return await self.__message_repo.create(
            source_id=source_id,
            source_type=source_type,
            sender_id=sender_id,
            text_content=text_content,
        )

    async def get(self, _id: UUID) -> Message:
        return await self.__message_repo.get(_id=_id)

    async def get_list(
        self, source_id: UUID, source_type: SourceType, offset: int = 0, limit: int = 50
    ) -> Sequence[Message]:
        return await self.__message_repo.get_list(
            source_id=source_id, source_type=source_type, offset=offset, limit=limit
        )
