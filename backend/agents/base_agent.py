from abc import ABC, abstractmethod
from pydantic import BaseModel


class BaseAgent(ABC):
    name: str

    @abstractmethod
    async def run(self, input_data: BaseModel) -> BaseModel:
        """Single public entry point for every agent."""
        ...
