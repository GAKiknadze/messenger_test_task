from datetime import datetime
from typing import Sequence
from uuid import UUID, uuid4

import pytest

from src.common.exceptions import ObjectNotFoundExc
from src.domain.messages import entities, repositories, services


class FakeMessageRepository:
    def __init__(self):
        self.messages = {}

    async def create(
        self,
        source_id: UUID,
        source_type: entities.SourceType,
        sender_id: UUID,
        text_content: str,
    ) -> entities.Message:
        message = entities.Message(
            id=uuid4(),
            source_id=source_id,
            source_type=source_type,
            sender_id=sender_id,
            text_content=text_content,
            created_at=datetime.now(),
        )
        self.messages[message.id] = message
        return message

    async def get(self, _id: UUID) -> entities.Message:
        if _id not in self.messages:
            raise ObjectNotFoundExc()
        return self.messages[_id]

    async def get_list(
        self,
        source_id: UUID,
        source_type: entities.SourceType,
        offset: int = 0,
        limit: int = 50,
    ) -> Sequence[entities.Message]:
        messages = [
            msg
            for msg in self.messages.values()
            if msg.source_id == source_id and msg.source_type == source_type
        ]
        return messages[offset: offset + limit]


@pytest.fixture
def message_repository() -> repositories.AbstractMessageRepository:
    return FakeMessageRepository()


@pytest.fixture
def message_service(message_repository) -> services.AbstractMessageService:
    return services.MessageService(message_repository)


class TestMessageService:
    async def test_send_message(self, message_service):
        source_id = uuid4()
        sender_id = uuid4()
        text = "Hello, world!"

        message = await message_service.send(
            source_id=source_id,
            source_type=entities.SourceType.CHAT,
            sender_id=sender_id,
            text_content=text,
        )

        assert isinstance(message, entities.Message)
        assert message.source_id == source_id
        assert message.source_type == entities.SourceType.CHAT
        assert message.sender_id == sender_id
        assert message.text_content == text
        assert message.created_at is not None
        assert message.readed_at is None

    async def test_get_message(self, message_service):
        source_id = uuid4()
        message = await message_service.send(
            source_id=source_id,
            source_type=entities.SourceType.CHAT,
            sender_id=uuid4(),
            text_content="Test message",
        )

        retrieved_message = await message_service.get(_id=message.id)
        assert retrieved_message == message

    async def test_get_nonexistent_message(self, message_service):
        with pytest.raises(ObjectNotFoundExc):
            await message_service.get(_id=uuid4())

    async def test_get_message_list(self, message_service):
        source_id = uuid4()
        source_type = entities.SourceType.GROUP

        messages = []
        for i in range(3):
            message = await message_service.send(
                source_id=source_id,
                source_type=source_type,
                sender_id=uuid4(),
                text_content=f"Message {i}",
            )
            messages.append(message)

        await message_service.send(
            source_id=uuid4(),
            source_type=source_type,
            sender_id=uuid4(),
            text_content="Different source",
        )

        retrieved_messages = await message_service.get_list(
            source_id=source_id, source_type=source_type
        )

        assert len(retrieved_messages) == 3
        for msg in messages:
            assert msg in retrieved_messages
