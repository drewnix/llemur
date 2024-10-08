from openai import OpenAI

from llemur.config import settings
from llemur.llm.llm_interface import (
    LLMInterface,  # Import from llm_interface to avoid circular imports
)


# ChatGPT (OpenAI) implementation
class OpenAILLM(LLMInterface):
    def __init__(self):
        self.client = None
        self.model_name = None

    def load_model(self, model_name: str):
        """
        Load the model by setting the model name. OpenAI's models are accessed
        via API, so no actual loading is needed.
        """
        available_models = ["gpt-3.5-turbo", "gpt-4", "gpt-4o"]
        if model_name not in available_models:
            raise ValueError(
                f"Model {model_name} is not available for ChatGPT. Choose from {available_models}."
            )

        self.model_name = model_name
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,  # Get API key from environment variable
        )
        print(f"Model {self.model_name} loaded for ChatGPT.")

    def generate_response(self, prompt: str) -> str:
        """
        Generate a response using the ChatGPT model.
        """
        if not self.model_name:
            raise RuntimeError("Model is not loaded. Call `load_model` first.")

        if not self.client:
            raise RuntimeError("OpenAI client is not initialized. Ensure API key is set.")

        try:
            # Create the chat completion
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ],
            )

            # Correctly access the message content in the response
            message_content = response.choices[0].message.content
            return message_content

        except Exception as e:
            raise RuntimeError(f"Failed to generate response: {e}")
