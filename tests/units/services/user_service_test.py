from datetime import datetime
from typing import Any, Dict
from uuid import UUID, uuid4

import pytest

from src.common.exceptions import AlreadyExistsExc, ObjectNotFoundExc
from src.domain.users import entities, repositories, services


class FakeUserRepository:
    def __init__(self):
        self.users = {}

    async def create(
        self, name: str, email: str, hashed_password: str
    ) -> entities.User:
        obj_id = uuid4()

        try:
            await self.get_by_email(email=email)
            raise AlreadyExistsExc()
        except ObjectNotFoundExc:
            pass

        user = entities.User(
            id=obj_id,
            name=name,
            email=email,
            hashed_password=hashed_password,
            created_at=datetime.now(),
        )
        self.users.update({obj_id: user})
        return user

    async def get(self, _id: UUID) -> entities.User:
        user = self.users.get(_id)
        if user is None:
            raise ObjectNotFoundExc()
        return user

    async def get_by_email(self, email: str) -> entities.User:
        for _, v in self.users.items():
            if v.email == email:
                return v
        raise ObjectNotFoundExc()

    async def update(self, _id: UUID, **attrs: Dict[str, Any]) -> entities.User:
        user = await self.get(_id)
        for k, v in attrs.items():
            if hasattr(user, k):
                setattr(user, k, v)
        user.updated_at = datetime.now()
        self.users.update({_id: user})
        return user

    async def delete(self, _id: UUID) -> None:
        if _id in self.users.keys():
            del self.users[_id]
        else:
            raise ObjectNotFoundExc()


@pytest.fixture
def user_repository() -> repositories.AbstractUserRepository:
    return FakeUserRepository()


@pytest.fixture
def user_service(user_repository) -> services.AbstractUserService:
    return services.UserService(user_repository)


class TestUserService:
    async def test_create_user(self, user_service):
        user = await user_service.create(
            name="Test User", email="test@example.com", hashed_password="password123"
        )
        assert user.name == "Test User"
        assert user.email == "test@example.com"
        assert user.hashed_password == "password123"

    async def test_create_duplicate_user(self, user_service):
        await user_service.create(
            name="Test User", email="test@example.com", hashed_password="password123"
        )

        with pytest.raises(AlreadyExistsExc):
            await user_service.create(
                name="Another User",
                email="test@example.com",
                hashed_password="password456",
            )

    async def test_get_user_by_id(self, user_service):
        created_user = await user_service.create(
            name="Test User", email="test@example.com", hashed_password="password123"
        )

        user = await user_service.get(created_user.id)
        assert user.id == created_user.id
        assert user.name == created_user.name
        assert user.email == created_user.email

    async def test_get_user_by_email(self, user_service):
        created_user = await user_service.create(
            name="Test User", email="test@example.com", hashed_password="password123"
        )

        user = await user_service.get_by_email("test@example.com")
        assert user.id == created_user.id
        assert user.name == created_user.name
        assert user.email == created_user.email

    async def test_update_user(self, user_service):
        user = await user_service.create(
            name="Test User", email="test@example.com", hashed_password="password123"
        )

        updated_user = await user_service.update(user.id, name="Updated User")
        assert updated_user.name == "Updated User"
        assert updated_user.email == "test@example.com"

    async def test_delete_user(self, user_service):
        user = await user_service.create(
            name="Test User", email="test@example.com", hashed_password="password123"
        )

        await user_service.delete(user.id)

        with pytest.raises(ObjectNotFoundExc):
            await user_service.get(user.id)
