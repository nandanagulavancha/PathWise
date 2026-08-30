from abc import ABC, abstractmethod


class LearningResourceProvider(ABC):
    @abstractmethod
    def search_resources(self, query: str, **kwargs) -> list[dict]:
        pass

    @abstractmethod
    def get_resource(self, external_id: str) -> dict | None:
        pass
