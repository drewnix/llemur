from anthropic import Anthropic

from llemur.config import settings
from llemur.llm.llm_interface import (
    LLMInterface,  # Import from llm_interface to avoid circular imports
)


# Anthropic Claude implementation
class AnthropicLLM(LLMInterface):
    def __init__(self):
        self.client = None
        self.model_name = None

    def load_model(self, model_name: str):
        """
        Set up the Anthropic client and load the model name.
        """
        available_models = ["claude-v1", "claude-v1.3", "claude-v2"]
        if model_name not in available_models:
            raise ValueError(
                f"Model {model_name} is not available for Anthropic. Choose from {available_models}."
            )

        # Set up the Anthropic client using the API key from the environment
        api_key = settings.ANTHROPIC_API_KEY
        if not api_key:
            raise RuntimeError(
                "Anthropic API key is not set. Set it in the environment variable `ANTHROPIC_API_KEY`."
            )

        self.client = Anthropic(api_key=api_key)

        self.model_name = model_name
        print(f"Model {self.model_name} loaded for Anthropic.")

    def generate_response(self, prompt: str) -> str:
        """
        Generate a response using the Claude model from Anthropic.
        """
        if not self.model_name:
            raise RuntimeError("Model is not loaded. Call `load_model` first.")

        try:
            # Send the prompt to the Claude model and receive a response
            response = self.client.completions.create(
                model=self.model_name,
                prompt=f"\n\nHuman: {prompt}\n\nAssistant:",
                max_tokens_to_sample=200,
            )
            return response.completion.strip()
        except Exception as e:
            raise RuntimeError(f"Failed to generate response: {e}")
