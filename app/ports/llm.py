import pydantic
from abc import ABC, abstractmethod


class LLm(ABC):
    @abstractmethod
    def run_completion(self, system_prompt: str, user_prompt: str, dto: type[pydantic.BaseModel]) -> pydantic.BaseModel:
        pass

    @abstractmethod
    async def run_completion_async(self, system_prompt: str, user_prompt: str, dto: type[pydantic.BaseModel]) -> pydantic.BaseModel:
        """Asynchronous counterpart of `run_completion` supporting non-blocking LLM calls"""
        pass