# File: llemur/llm/llm_base.py

from llemur.llm.anthropic_llm import AnthropicLLM
from llemur.llm.llm_interface import LLMInterface
from llemur.llm.local_llm import LocalLLM
from llemur.llm.openai_llm import OpenAILLM


class LLMFactory:
    @staticmethod
    def get_provider(provider_name: str) -> LLMInterface:
        if provider_name == "local":
            return LocalLLM()
        elif provider_name == "openai":
            return OpenAILLM()
        elif provider_name == "anthropic":
            return AnthropicLLM()
        else:
            raise ValueError(f"Unknown provider: {provider_name}")


def load_llm(llm_provider: str, model_name: str):
    """
    Load the appropriate LLM provider and model.

    Args:
        llm_provider (str): The LLM provider (e.g., 'openai', 'anthropic', 'local').
        model_name (str): The name of the model to use.

    Returns:
        LLMInterface: An instance of the selected LLM.
    """
    # Load the correct LLM provider
    llm = LLMFactory.get_provider(llm_provider)

    # Load the model
    llm.load_model(model_name)

    return llm
