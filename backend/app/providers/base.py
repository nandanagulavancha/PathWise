from abc import ABC, abstractmethod


class LearningResourceProvider(ABC):
    @abstractmethod
    async def search_resources(self, query: str, **kwargs) -> list[dict]:
        pass

    @abstractmethod
    async def get_resource(self, external_id: str) -> dict | None:
        pass
