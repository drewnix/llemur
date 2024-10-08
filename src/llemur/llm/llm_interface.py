from abc import ABC, abstractmethod


# Common interface for LLMs
class LLMInterface(ABC):
    @abstractmethod
    def load_model(self, model_name: str):
        pass

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        pass
