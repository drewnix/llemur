from pathlib import Path
from typing import Optional

import typer

from llemur.llm.llm_base import load_llm

app = typer.Typer()

# Define mappings for file extensions to programming languages
LANGUAGE_MAP = {".py": "python", ".rs": "rust", ".ts": "typescript", ".js": "javascript"}


# Base directory for prompts relative to the script location
BASE_DIR = Path(__file__).resolve().parent  # Directory where the Python script is located
PROMPTS_DIR = BASE_DIR / "prompts"  # Path to the 'prompts' directory relative to the script


def perf_analysis(
    file_name: str = typer.Option(..., "--file", help="File to run a perf analysis on"),
    output: str = typer.Option(
        "perf_analysis_prompt.txt", "--output", help="File to dump the performance analysis prompt"
    ),
    llm: str = typer.Option(
        "openai",
        "--llm",
        help="Specify the LLM provider to use (e.g., 'openai', 'local', 'anthropic')",
    ),
    model: str = typer.Option(
        "gpt-4o", "--model", help="Specify the model to use (e.g., 'gpt-4', 'claude-v2')"
    ),
):
    """
    Perform a performance analysis of the specified file.
    Detects the language, loads the appropriate prompt, and writes the final prompt to an output file.
    """
    file_path = Path(file_name)

    # Step 1: Detect the programming language
    language = detect_language(file_path)

    if not language:
        typer.echo(f"Unsupported file type for {file_path}")
        raise typer.Exit(code=1)

    typer.echo(f"Detected language: {language}")

    # Step 2: Load the corresponding performance analysis prompt template
    prompt_template_path = PROMPTS_DIR / f"perf_analysis_{language}.prompt"

    if not prompt_template_path.exists():
        typer.echo(f"Prompt template for {language} not found at {prompt_template_path}")
        raise typer.Exit(code=1)

    prompt_template = load_prompt_template(prompt_template_path)

    # Step 3: Read the target code from the file
    try:
        with open(file_path, "r", encoding="utf-8") as code_file:
            code_content = code_file.read()
    except Exception as e:
        typer.echo(f"Error reading file {file_path}: {e}")
        raise typer.Exit(code=1)

    # Step 4: Create the final prompt by embedding the code in the template
    final_prompt = prompt_template.replace("{{CODE}}", code_content)

    # Step 5: Load the LLM and model
    llm_instance = load_llm(llm, model)

    # Step 5: Write the final prompt to the output file
    try:
        with open(output, "w", encoding="utf-8") as output_file:
            output_file.write(final_prompt)
        typer.echo(f"Performance analysis prompt written to {output}")
    except Exception as e:
        typer.echo(f"Error writing to output file {output}: {e}")
        raise typer.Exit(code=1)

    # Step 6: Ask the user if they want to send the prompt to the LLM
    if typer.confirm("Would you like to send the prompt to the selected LLM for analysis?"):
        # Step 7: Load the LLM and model
        llm_instance = load_llm(llm, model)

        # Step 8: Send the prompt to the LLM and capture the response
        try:
            response = llm_instance.generate_response(final_prompt)
            typer.echo(f"Response received from {model}: {response}")
        except Exception as e:
            typer.echo(f"Error sending prompt to LLM: {e}")
            raise typer.Exit(code=1)

        # Step 9: Ask the user where to save the LLM response
        output_response_file = typer.prompt(
            "Please specify the file name to save the LLM's response",
            default="perf_analysis_response.txt",
        )

        # Step 10: Write the LLM response to the specified file
        try:
            with open(output_response_file, "w", encoding="utf-8") as response_file:
                response_file.write(response)
            typer.echo(f"LLM response saved to {output_response_file}")
        except Exception as e:
            typer.echo(f"Error writing LLM response to file {output_response_file}: {e}")
            raise typer.Exit(code=1)
    else:
        typer.echo("Prompt not sent to LLM.")


def detect_language(file_path: Path) -> Optional[str]:
    """
    Detects the programming language based on the file extension.
    Args:
        file_path (Path): The path to the file.

    Returns:
        str: The detected programming language (e.g., "python"), or None if unsupported.
    """
    extension = file_path.suffix
    return LANGUAGE_MAP.get(extension)


def load_prompt_template(template_path: Path) -> str:
    """
    Loads the performance analysis prompt template from a file.
    Args:
        template_path (Path): The path to the prompt template file.

    Returns:
        str: The contents of the template.
    """
    try:
        with open(template_path, "r", encoding="utf-8") as template_file:
            return template_file.read()
    except Exception as e:
        typer.echo(f"Error loading prompt template: {e}")
        raise typer.Exit(code=1)
