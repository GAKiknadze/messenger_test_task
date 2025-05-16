from dataclasses import dataclass
from datetime import datetime
from enum import Enum, IntFlag
from uuid import UUID


class ChatType(str, Enum):
    PERSONAL = "personal"
    GROUP = "group"


@dataclass
class Chat:
    id: UUID
    chat_type: ChatType
    title: str
    created_at: datetime
    updated_at: datetime


class ChatMemberPermissions(IntFlag):
    MESSAGE_ADD = 10
    MESSAGE_GET = 11
    MEMBER_ADD = 20
    MEMBER_REMOVE = 21
    MEMBER_BLOCK = 22
    MEMBER_CHANGE_ROLE = 23
    CHAT_CHANGE = 30
    CHAT_DELETE = 31
    ROLE_BLOCKED = 0
    ROLE_DEFAULT = MESSAGE_ADD | MESSAGE_GET
    ROLE_ADMIN = ROLE_DEFAULT | MEMBER_ADD | MEMBER_BLOCK
    ROLE_OWNER = (
        ROLE_ADMIN | MEMBER_REMOVE | MEMBER_CHANGE_ROLE | CHAT_CHANGE | CHAT_DELETE
    )


@dataclass
class ChatMember:
    chat_id: UUID
    user_id: UUID
    permissions: ChatMemberPermissions
    invited_by: UUID | None = None
    joined_at: datetime | None = None
