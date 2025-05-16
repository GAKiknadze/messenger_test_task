from typing import Protocol, Sequence
from uuid import UUID

from ...common.exceptions import AccessDeniedExc
from .entities import Chat, ChatType, ChatMember, ChatMemberPermissions
from .repositories import AbstractChatRepository, AbstractChatMemberRepository


class AbstractChatService(Protocol):
    async def create_personal(self, title: str, owner_user_1: UUID, owner_user_2: UUID) -> Chat:
        """Создать личный чат между двумя пользователями

        Args:
            title (str): Название чата
            owner_user_1 (UUID): ID первого владельца
            owner_user_2 (UUID): ID второго владельца

        Returns:
            Chat: Объект чата
        """
        ...

    async def create_group(self, title: str, owner_id: UUID) -> Chat:
        """Создать групповой чат

        Args:
            title (str): Название чата
            owner_id (UUID): ID владельца группы

        Returns:
            Chat: Объект чата
        """
        ...

    async def get(self, chat_id: UUID) -> Chat:
        """Получить чат по его идентификатору

        Args:
            chat_id (UUID): Идентификатор чата

        Returns:
            Chat: Объект чата

        Raises:
            ObjectNotFoundExc: Чат не найден
        """
        ...

    async def update(self, chat_id: UUID, executor_id: UUID | None = None, title: str | None = None) -> Chat:
        """Обновить данные чата

        Args:
            chat_id (UUID): Идентификатор чата
            executor_id (UUID | None, optional): ID пользователя, выполняющего обновление
            title (str | None, optional): Новое название чата

        Returns:
            Chat: Обновленный объект чата

        Raises:
            ObjectNotFoundExc: Чат не найден
            AccessDeniedExc: Нет прав на изменение чата
        """
        ...

    async def delete(self, chat_id: UUID, executor_id: UUID | None = None) -> None:
        """Удалить чат

        Args:
            chat_id (UUID): Идентификатор чата
            executor_id (UUID | None, optional): ID пользователя, выполняющего удаление

        Raises:
            ObjectNotFoundExc: Чат не найден
            AccessDeniedExc: Нет прав на удаление чата
        """
        ...

    async def get_list(self, user_id: UUID, offset: int = 0, limit: int = 50) -> Sequence[UUID]:
        """Получить список чатов пользователя

        Args:
            user_id (UUID): ID пользователя
            offset (int, optional): Смещение. Defaults to 0.
            limit (int, optional): Лимит. Defaults to 50.

        Returns:
            Sequence[UUID]: Список ID чатов пользователя
        """
        ...

    async def member_add(self, chat_id: UUID, user_id: UUID, executor_id: UUID | None = None) -> ChatMember:
        """Добавить пользователя в чат

        Args:
            chat_id (UUID): ID чата
            user_id (UUID): ID добавляемого пользователя
            executor_id (UUID | None, optional): ID пользователя, выполняющего добавление

        Returns:
            ChatMember: Объект участника чата

        Raises:
            ObjectNotFoundExc: Чат не найден
            AccessDeniedExc: Нет прав на добавление участников
        """
        ...

    async def member_remove(self, chat_id: UUID, user_id: UUID, executor_id: UUID | None = None) -> None:
        """Удалить пользователя из чата

        Args:
            chat_id (UUID): ID чата
            user_id (UUID): ID удаляемого пользователя
            executor_id (UUID | None, optional): ID пользователя, выполняющего удаление

        Raises:
            ObjectNotFoundExc: Чат или участник не найден
            AccessDeniedExc: Нет прав на удаление участников
        """
        ...

    async def member_block(self, chat_id: UUID, user_id: UUID, executor_id: UUID | None = None) -> None:
        """Заблокировать пользователя в чате

        Args:
            chat_id (UUID): ID чата
            user_id (UUID): ID блокируемого пользователя
            executor_id (UUID | None, optional): ID пользователя, выполняющего блокировку

        Raises:
            ObjectNotFoundExc: Чат или участник не найден
            AccessDeniedExc: Нет прав на блокировку участников
        """
        ...

    async def member_unblock(self, chat_id: UUID, user_id: UUID, executor_id: UUID | None = None) -> None:
        """Разблокировать пользователя в чате

        Args:
            chat_id (UUID): ID чата
            user_id (UUID): ID разблокируемого пользователя
            executor_id (UUID | None, optional): ID пользователя, выполняющего разблокировку

        Raises:
            ObjectNotFoundExc: Чат или участник не найден
            AccessDeniedExc: Нет прав на разблокировку участников
        """
        ...

    async def member_change_role(self, chat_id: UUID, user_id: UUID, permissions: ChatMemberPermissions, executor_id: UUID | None = None) -> None:
        """Изменить роль пользователя в чате

        Args:
            chat_id (UUID): ID чата
            user_id (UUID): ID пользователя
            permissions (ChatMemberPermissions): Новые права пользователя
            executor_id (UUID | None, optional): ID пользователя, выполняющего изменение роли

        Raises:
            ObjectNotFoundExc: Чат или участник не найден
            AccessDeniedExc: Нет прав на изменение ролей
        """
        ...

    async def member_get(self, chat_id: UUID, user_id: UUID) -> ChatMember:
        """Получить участника чата

        Args:
            chat_id (UUID): ID чата
            user_id (UUID): ID пользователя

        Returns:
            ChatMember: Объект участника чата

        Raises:
            ObjectNotFoundExc: Участник не найден
        """
        ...


class ChatService:
    def __init__(self, chat_repository: AbstractChatRepository, chat_member_repository: AbstractChatMemberRepository):
        self.__chat_repo = chat_repository
        self.__chat_member_repo = chat_member_repository

    async def create_personal(self, title: str, owner_user_1: UUID, owner_user_2: UUID) -> Chat:
        chat = await self.__chat_repo.create(chat_type=ChatType.PERSONAL, title=title)
        await self.__chat_member_repo.create(
            ChatMember(
                chat_id=chat.id,
                user_id=owner_user_1,
                permissions=ChatMemberPermissions.ROLE_OWNER
            )
        )
        await self.__chat_member_repo.create(
            ChatMember(
                chat_id=chat.id,
                user_id=owner_user_2,
                permissions=ChatMemberPermissions.ROLE_OWNER
            )
        )
        return chat
    
    async def create_group(self, title: str, owner_id: UUID) -> Chat:
        chat = await self.__chat_repo.create(
            chat_type=ChatType.GROUP,
            title=title
        )
        await self.__chat_member_repo.create(
            ChatMember(
                chat_id=chat.id,
                user_id=owner_id,
                permissions=ChatMemberPermissions.ROLE_OWNER
            )
        )
        return chat

    async def _can_execute(self, chat_id: UUID, user_id: UUID, action: ChatMemberPermissions) -> bool:
        member = await self.__chat_member_repo.get((chat_id, user_id))
        return action in member.permissions or action == member.permissions

    async def get(self, chat_id: UUID) -> Chat:
        return await self.__chat_repo.get(_id=chat_id)

    async def update(self, chat_id: UUID, executor_id: UUID | None = None, title: str | None = None) -> Chat:
        if executor_id is not None and not await self._can_execute(chat_id, executor_id, ChatMemberPermissions.CHAT_CHANGE):
            raise AccessDeniedExc()
        return await self.__chat_repo.update(_id=chat_id, title=title)

    async def delete(self, chat_id: UUID, executor_id: UUID | None = None) -> None:
        if executor_id is not None and not await self._can_execute(chat_id, executor_id, ChatMemberPermissions.CHAT_DELETE):
            raise AccessDeniedExc()
        await self.__chat_repo.delete(_id=chat_id)
    
    async def get_list(self, user_id: UUID, offset: int = 0, limit:  int = 50) -> Sequence[UUID]:
        return await self.__chat_member_repo.list_by_user_id(_id=user_id, offset=offset, limit=limit)
    
    async def member_get(self, chat_id: UUID, user_id: UUID) -> ChatMember:
        return await self.__chat_member_repo.get((chat_id, user_id))
    
    async def member_add(self, chat_id: UUID, user_id: UUID, executor_id: UUID | None = None) -> ChatMember:
        if executor_id is not None and not await self._can_execute(chat_id, executor_id, ChatMemberPermissions.MEMBER_ADD):
            raise AccessDeniedExc()
        return await self.__chat_member_repo.create(
            ChatMember(
                chat_id=chat_id,
                user_id=user_id,
                permissions=ChatMemberPermissions.ROLE_DEFAULT,
                invited_by=executor_id
            )
        )
    
    async def member_remove(self, chat_id: UUID, user_id: UUID, executor_id: UUID | None = None) -> None:
        if executor_id is not None and not await self._can_execute(chat_id, executor_id, ChatMemberPermissions.MEMBER_REMOVE):
            raise AccessDeniedExc()
        await self.__chat_member_repo.delete((chat_id, user_id))
    
    async def member_block(self, chat_id: UUID, user_id: UUID, executor_id: UUID | None = None) -> None:
        if executor_id is not None and not await self._can_execute(chat_id, executor_id, ChatMemberPermissions.MEMBER_BLOCK):
            raise AccessDeniedExc()
        await self.__chat_member_repo.update((chat_id, user_id), permissions=ChatMemberPermissions.ROLE_BLOCKED)
    
    async def member_unblock(self, chat_id: UUID, user_id: UUID, executor_id: UUID | None = None) -> None:
        if executor_id is not None and not await self._can_execute(chat_id, executor_id, ChatMemberPermissions.MEMBER_BLOCK):
            raise AccessDeniedExc()
        await self.__chat_member_repo.update((chat_id, user_id), permissions=ChatMemberPermissions.ROLE_DEFAULT)
    
    async def member_change_role(self, chat_id: UUID, user_id: UUID, permissions: ChatMemberPermissions, executor_id: UUID | None = None) -> None:
        if executor_id is not None and not await self._can_execute(chat_id, executor_id, ChatMemberPermissions.MEMBER_CHANGE_ROLE):
            raise AccessDeniedExc()
        await self.__chat_member_repo.update((chat_id, user_id), permissions=permissions)
