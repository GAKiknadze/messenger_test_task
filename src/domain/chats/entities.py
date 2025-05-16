from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID


class ChatType(str, Enum):
    PRIVATE = "private"
    GROUP = "group"


@dataclass
class Chat:
    id: UUID
    chat_type: ChatType
    title: str
    created_at: datetime
    updated_at: datetime
