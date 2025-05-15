from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID


class SourceType(str, Enum):
    CHAT = "chat"
    GROUP = "group"


@dataclass
class Message:
    id: UUID
    source_id: UUID
    source_type: SourceType
    sender_id: UUID
    text_content: str
    created_at: datetime
    readed_at: datetime | None = None
