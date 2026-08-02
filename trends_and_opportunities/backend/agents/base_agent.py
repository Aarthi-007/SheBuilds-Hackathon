"""
BaseAgent — abstract contract every Klyro agent inherits.
Rule (context.md §7 / §15): every agent exposes exactly ONE public method: run().
All helper logic must be private (prefixed with _).
"""

from abc import ABC, abstractmethod
from pydantic import BaseModel


class BaseAgent(ABC):
    name: str

    @abstractmethod
    async def run(self, input_data: BaseModel) -> BaseModel:
        """Single public entrypoint. Takes a typed Pydantic input, returns a typed Pydantic output."""
        raise NotImplementedError
