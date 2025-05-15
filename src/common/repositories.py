from typing import Protocol, TypeVar

T_ID = TypeVar("T_ID", contravariant=True)
T_OBJ = TypeVar("T_OBJ", covariant=True)


class AbstractCreate(Protocol[T_OBJ]):
    async def create(self, **attrs) -> T_OBJ:
        """Создать объект

        Kwargs:
            **attrs (Dict[str, Any]): Параметры объекта

        Returns:
            T_OBJ: Объект

        Raises:
            AlreadyExistsExc: Объект с уникальными полями уже существует
        """
        ...


class AbstractGet(Protocol[T_ID, T_OBJ]):
    async def get(self, _id: T_ID) -> T_OBJ:
        """Получить объект

        Args:
            _id (T_ID): Идентификатор объекта

        Returns:
            T_OBJ: Объект

        Raises:
            ObjectNotFoundExc: Объект не найден
        """
        ...


class AbstractUpdate(Protocol[T_ID, T_OBJ]):
    async def update(self, _id: T_ID, **attrs) -> T_OBJ:
        """Обновить объект

        Args:
            _id (T_ID): Идентификатор объекта

        Kwargs:
            **attrs (Dict[str, Any]): Измененные параметры объекта

        Returns:
            T_OBJ: Объект

        Raises:
            ObjectNotFoundExc: Объект не найден
            AlreadyExistsExc: Объект с уникальными полями уже существует
        """
        ...


class AbstractDelete(Protocol[T_ID, T_OBJ]):
    async def delete(self, _id: T_ID) -> None:
        """Удалить объект

        Args:
            _id (T_ID): Идентификатор объекта

        Raises:
            ObjectNotFoundExc: Объект не найден
        """
        ...
