import openai
import pydantic
import time
from app import ports
from app.logging import get_logger

# Create logger for this module
logger = get_logger(__name__)


class OpenAIAdapter(ports.LLm):
    def __init__(self, api_key: str, model: str) -> None:
        self._model = model
        logger.info(f"Initializing OpenAI adapter with model: {model}")
        self._client = openai.OpenAI(api_key=api_key)
        self._aclient = openai.AsyncOpenAI(api_key=api_key)
        logger.debug("OpenAI clients initialized")

    def run_completion(self, system_prompt: str, user_prompt: str, dto: type[pydantic.BaseModel]) -> pydantic.BaseModel:
        """
        Executes a completion request using the OpenAI API with the provided prompts and response format.
    
        Args:
            system_prompt (str): The system's introductory message for the chat.
            user_prompt (str): The user input for which a response is needed.
            dto (Type[pydantic.BaseModel]): A Pydantic model class used to define the structure of the API response.
    
        Returns:
            pydantic.BaseModel: An instance of the provided DTO class populated with the API response data.
            more info: https://platform.openai.com/docs/guides/structured-outputs?api-mode=chat
        """
        logger.info(f"Running completion with model: {self._model}")
        logger.debug(f"DTO class: {dto.__name__}")
        
        start_time = time.time()
        try:
            completion = self._client.beta.chat.completions.parse(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format=dto
            )
            elapsed_time = time.time() - start_time
            logger.info(f"OpenAI completion successful in {elapsed_time:.2f}s")
            return completion.choices[0].message.parsed
        except Exception as e:
            logger.error(f"OpenAI completion failed: {str(e)}")
            raise

    async def run_completion_async(self, system_prompt: str, user_prompt: str,
                                   dto: type[pydantic.BaseModel]) -> pydantic.BaseModel:
        """
        Executes a completion request using the OpenAI API with the provided prompts and response format.

        Args:
            system_prompt (str): The system's introductory message for the chat.
            user_prompt (str): The user input for which a response is needed.
            dto (Type[pydantic.BaseModel]): A Pydantic model class used to define the structure of the API response.

        Returns:
         pydantic.BaseModel: An instance of the provided DTO class populated with the API response data.

         more info: https://platform.openai.com/docs/guides/structured-outputs?api-mode=chat
         """
        logger.info(f"Running async completion with model: {self._model}")
        logger.debug(f"DTO class: {dto.__name__}")
        
        start_time = time.time()
        try:
            completion = await self._aclient.beta.chat.completions.parse(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format=dto
            )
            elapsed_time = time.time() - start_time
            logger.info(f"Async OpenAI completion successful in {elapsed_time:.2f}s")
            return completion.choices[0].message.parsed
        except Exception as e:
            logger.error(f"Async OpenAI completion failed: {str(e)}")
            raise
