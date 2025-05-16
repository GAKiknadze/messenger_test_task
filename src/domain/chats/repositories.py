from typing import Protocol, Tuple, Sequence
from uuid import UUID

from ...common.repositories import AbstractDelete, AbstractGet, AbstractUpdate, AbstractCreate
from .entities import Chat, ChatType, ChatMember


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

MEMBER_ID = Tuple[UUID, UUID]

class AbstractChatMemberRepository(
    AbstractCreate[ChatMember],
    AbstractGet[MEMBER_ID, ChatMember],
    AbstractUpdate[MEMBER_ID, ChatMember],
    AbstractDelete[MEMBER_ID, ChatMember],
    Protocol
):
    async def list_by_user_id(_id: UUID, offset: int = 0, limit:  int = 50) -> Sequence[UUID]:
        """Получить список идентификаторов чатов, связанных с конкретным пользователем.

        Args:
            _id (UUID): Уникальный идентификатор пользователя.
            offset (int, optional): Количество пропускаемых записей. По умолчанию 0.
            limit (int, optional): Максимальное количество возвращаемых записей. По умолчанию 50.

        Returns:
            Sequence[UUID]: Последовательность UUID чатов, в которых участвует пользователь.
        """
        
        ...
