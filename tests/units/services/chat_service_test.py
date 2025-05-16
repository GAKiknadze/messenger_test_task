from datetime import datetime
from typing import Any, Dict, Sequence
from uuid import UUID, uuid4

import pytest

from src.common.exceptions import AccessDeniedExc, ObjectNotFoundExc
from src.domain.chats import entities, repositories, services


class FakeChatRepository:
    def __init__(self):
        self.chats = {}

    async def create(self, chat_type: entities.ChatType, title: str) -> entities.Chat:
        chat = entities.Chat(
            id=uuid4(),
            chat_type=chat_type,
            title=title,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        self.chats[chat.id] = chat
        return chat

    async def get(self, _id: UUID) -> entities.Chat:
        if _id not in self.chats:
            raise ObjectNotFoundExc("Chat not found")
        return self.chats[_id]

    async def update(self, _id: UUID, **attrs: Dict[str, Any]) -> entities.Chat:
        chat = await self.get(_id)
        for k, v in attrs.items():
            if v is not None and hasattr(chat, k):
                setattr(chat, k, v)
        chat.updated_at = datetime.now()
        self.chats[_id] = chat
        return chat

    async def delete(self, _id: UUID) -> None:
        if _id not in self.chats:
            raise ObjectNotFoundExc("Chat not found")
        del self.chats[_id]


class FakeChatMemberRepository:
    def __init__(self):
        self.members = {}

    async def create(self, obj: entities.ChatMember) -> entities.ChatMember:
        member_id = (obj.chat_id, obj.user_id)
        if member_id in self.members:
            return self.members[member_id]
        obj.joined_at = datetime.now()
        self.members[member_id] = obj
        return obj

    async def get(self, _id: tuple[UUID, UUID]) -> entities.ChatMember:
        if _id not in self.members:
            raise ObjectNotFoundExc("Member not found")
        return self.members[_id]

    async def update(
        self, _id: tuple[UUID, UUID], **attrs: Dict[str, Any]
    ) -> entities.ChatMember:
        member = await self.get(_id)
        for k, v in attrs.items():
            if v is not None and hasattr(member, k):
                setattr(member, k, v)
        self.members[_id] = member
        return member

    async def delete(self, _id: tuple[UUID, UUID]) -> None:
        if _id not in self.members:
            raise ObjectNotFoundExc("Member not found")
        del self.members[_id]

    async def list_by_user_id(
        self, _id: UUID, offset: int = 0, limit: int = 50
    ) -> Sequence[UUID]:
        chat_ids = [
            chat_id for chat_id, user_id in self.members.keys() if user_id == _id
        ]
        return chat_ids[offset : offset + limit]


@pytest.fixture
def chat_repository() -> repositories.AbstractChatRepository:
    return FakeChatRepository()


@pytest.fixture
def chat_member_repository() -> repositories.AbstractChatMemberRepository:
    return FakeChatMemberRepository()


@pytest.fixture
def chat_service(
    chat_repository, chat_member_repository
) -> services.AbstractChatService:
    return services.ChatService(chat_repository, chat_member_repository)


class TestChatService:
    async def test_create_personal_chat(self, chat_service):
        user1_id = uuid4()
        user2_id = uuid4()
        chat = await chat_service.create_personal(
            title="Test Personal Chat",
            owner_user_1=user1_id,
            owner_user_2=user2_id,
        )
        assert isinstance(chat, entities.Chat)
        assert chat.chat_type == entities.ChatType.PERSONAL
        assert chat.title == "Test Personal Chat"

    async def test_create_group_chat(self, chat_service):
        owner_id = uuid4()
        chat = await chat_service.create_group(
            title="Test Group Chat",
            owner_id=owner_id,
        )
        assert isinstance(chat, entities.Chat)
        assert chat.chat_type == entities.ChatType.GROUP
        assert chat.title == "Test Group Chat"

    async def test_get_chat(self, chat_service):
        owner_id = uuid4()
        created_chat = await chat_service.create_group(
            title="Test Group",
            owner_id=owner_id,
        )

        chat = await chat_service.get(chat_id=created_chat.id)
        assert chat.id == created_chat.id
        assert chat.title == "Test Group"

    async def test_get_nonexistent_chat(self, chat_service):
        with pytest.raises(ObjectNotFoundExc):
            await chat_service.get(chat_id=uuid4())

    async def test_update_chat_with_permissions(self, chat_service):
        owner_id = uuid4()
        created_chat = await chat_service.create_group(
            title="Original Title",
            owner_id=owner_id,
        )

        updated_chat = await chat_service.update(
            chat_id=created_chat.id, executor_id=owner_id, title="Updated Title"
        )
        assert updated_chat.id == created_chat.id
        assert updated_chat.title == "Updated Title"

    async def test_update_chat_without_permissions(self, chat_service):
        owner_id = uuid4()
        non_owner_id = uuid4()
        created_chat = await chat_service.create_group(
            title="Original Title",
            owner_id=owner_id,
        )

        await chat_service.member_add(
            chat_id=created_chat.id, user_id=non_owner_id, executor_id=owner_id
        )

        with pytest.raises(AccessDeniedExc):
            await chat_service.update(
                chat_id=created_chat.id, executor_id=non_owner_id, title="Updated Title"
            )

    async def test_delete_chat_with_permissions(self, chat_service):
        owner_id = uuid4()
        created_chat = await chat_service.create_group(
            title="To Be Deleted",
            owner_id=owner_id,
        )

        await chat_service.delete(chat_id=created_chat.id, executor_id=owner_id)

        with pytest.raises(ObjectNotFoundExc):
            await chat_service.get(chat_id=created_chat.id)

    async def test_delete_chat_without_permissions(self, chat_service):
        owner_id = uuid4()
        non_owner_id = uuid4()
        created_chat = await chat_service.create_group(
            title="To Be Deleted",
            owner_id=owner_id,
        )

        await chat_service.member_add(
            chat_id=created_chat.id, user_id=non_owner_id, executor_id=owner_id
        )

        with pytest.raises(AccessDeniedExc):
            await chat_service.delete(chat_id=created_chat.id, executor_id=non_owner_id)

    async def test_get_chat_list(self, chat_service):
        user_id = uuid4()
        chat1 = await chat_service.create_group(title="Chat 1", owner_id=user_id)
        chat2 = await chat_service.create_group(title="Chat 2", owner_id=user_id)

        chat_ids = await chat_service.get_list(user_id=user_id)
        assert len(chat_ids) == 2
        assert chat1.id in chat_ids
        assert chat2.id in chat_ids

    async def test_member_operations(self, chat_service, chat_member_repository):
        owner_id = uuid4()
        user_id = uuid4()
        chat = await chat_service.create_group(title="Test Group", owner_id=owner_id)

        member = await chat_service.member_add(
            chat_id=chat.id, user_id=user_id, executor_id=owner_id
        )
        assert member.chat_id == chat.id
        assert member.user_id == user_id
        assert member.permissions == entities.ChatMemberPermissions.ROLE_DEFAULT

        await chat_service.member_block(
            chat_id=chat.id, user_id=user_id, executor_id=owner_id
        )
        blocked_member = await chat_member_repository.get((chat.id, user_id))
        assert blocked_member.permissions == entities.ChatMemberPermissions.ROLE_BLOCKED

        await chat_service.member_unblock(
            chat_id=chat.id, user_id=user_id, executor_id=owner_id
        )
        unblocked_member = await chat_member_repository.get((chat.id, user_id))
        assert (
            unblocked_member.permissions == entities.ChatMemberPermissions.ROLE_DEFAULT
        )

        await chat_service.member_remove(
            chat_id=chat.id, user_id=user_id, executor_id=owner_id
        )
        with pytest.raises(ObjectNotFoundExc):
            await chat_member_repository.get((chat.id, user_id))

    async def test_member_get(self, chat_service):
        owner_id = uuid4()
        user_id = uuid4()
        chat = await chat_service.create_group(title="Test Group", owner_id=owner_id)

        await chat_service.member_add(
            chat_id=chat.id, user_id=user_id, executor_id=owner_id
        )

        member = await chat_service.member_get(chat_id=chat.id, user_id=user_id)
        assert member.chat_id == chat.id
        assert member.user_id == user_id
        assert member.permissions == entities.ChatMemberPermissions.ROLE_DEFAULT

        with pytest.raises(ObjectNotFoundExc):
            await chat_service.member_get(chat_id=chat.id, user_id=uuid4())
