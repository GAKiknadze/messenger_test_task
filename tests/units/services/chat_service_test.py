from datetime import datetime
from uuid import UUID, uuid4
from typing import Any, Dict

import pytest

from src.common.exceptions import ObjectNotFoundExc
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
            if hasattr(chat, k):
                setattr(chat, k, v)
        chat.updated_at = datetime.now()
        self.chats.update({_id: chat})
        return chat

    async def delete(self, _id: UUID) -> None:
        if _id not in self.chats:
            raise ObjectNotFoundExc("Chat not found")
        del self.chats[_id]


@pytest.fixture
def chat_repository() -> repositories.AbstractChatRepository:
    return FakeChatRepository()


@pytest.fixture
def chat_service(chat_repository) -> services.AbstractChatService:
    return services.ChatService(chat_repository)


class TestChatService:
    async def test_create_chat(self, chat_service):
        chat = await chat_service.create(
            chat_type=entities.ChatType.PRIVATE, title="Test Chat"
        )
        assert isinstance(chat, entities.Chat)
        assert chat.chat_type == entities.ChatType.PRIVATE
        assert chat.title == "Test Chat"

    async def test_get_chat(self, chat_service):
        created_chat = await chat_service.create(
            chat_type=entities.ChatType.GROUP, title="Test Group"
        )

        chat = await chat_service.get(_id=created_chat.id)
        assert chat.id == created_chat.id
        assert chat.title == "Test Group"

    async def test_get_nonexistent_chat(self, chat_service):
        with pytest.raises(ObjectNotFoundExc):
            await chat_service.get(_id=uuid4())

    async def test_update_chat(self, chat_service):
        created_chat = await chat_service.create(
            chat_type=entities.ChatType.PRIVATE, title="Original Title"
        )

        updated_chat = await chat_service.update(
            _id=created_chat.id, title="Updated Title"
        )
        assert updated_chat.id == created_chat.id
        assert updated_chat.title == "Updated Title"

    async def test_update_nonexistent_chat(self, chat_service):
        with pytest.raises(ObjectNotFoundExc):
            await chat_service.update(_id=uuid4(), title="New Title")

    async def test_delete_chat(self, chat_service):
        created_chat = await chat_service.create(
            chat_type=entities.ChatType.PRIVATE, title="To Be Deleted"
        )

        await chat_service.delete(_id=created_chat.id)

        with pytest.raises(ObjectNotFoundExc):
            await chat_service.get(_id=created_chat.id)

    async def test_delete_nonexistent_chat(self, chat_service):
        with pytest.raises(ObjectNotFoundExc):
            await chat_service.delete(_id=uuid4())
