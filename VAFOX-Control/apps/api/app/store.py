"""Temporary in-memory repositories for the local-only V1 application.

Production persistence is intentionally not wired. PostgreSQL DDL is maintained
in infra/postgres and will be adopted through a reviewed persistence adapter.
"""
from collections.abc import Iterable
from typing import Generic, TypeVar
from uuid import UUID

T = TypeVar("T")


class RegistryStore(Generic[T]):
    def __init__(self) -> None:
        self._items: dict[UUID, T] = {}

    def create(self, item: T) -> T:
        self._items[item.id] = item
        return item

    def list(self) -> Iterable[T]:
        return self._items.values()

    def get(self, item_id: UUID) -> T | None:
        return self._items.get(item_id)

    def replace(self, item: T) -> T:
        self._items[item.id] = item
        return item


servers = RegistryStore()
services = RegistryStore()
deployments = RegistryStore()
