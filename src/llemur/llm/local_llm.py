from transformers import AutoModelForCausalLM, AutoTokenizer

from llemur.llm.llm_interface import (
    LLMInterface,  # Import from llm_interface to avoid circular imports
)


class LocalLLM(LLMInterface):
    def __init__(self):
        self.model = None
        self.tokenizer = None

    def load_model(self, model_name: str):
        """
        Load a Hugging Face model either from local storage or from the Hugging Face hub.
        """
        try:
            print(f"Loading model: {model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
        except Exception as e:
            raise RuntimeError(f"Failed to load model {model_name}: {e}")

    def generate_response(self, prompt: str) -> str:
        """
        Generate a response using the loaded model based on the input prompt.
        """
        if not self.model or not self.tokenizer:
            raise RuntimeError("Model is not loaded. Call `load_model` first.")

        # Tokenize input and generate output using the model
        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(inputs["input_ids"], max_length=200)

        # Decode output and return response
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return response
