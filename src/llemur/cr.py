import subprocess

import typer
from rich.console import Console

console = Console()


def cr(
    send: bool = typer.Option(False, "--send", help="Send to OpenAI for code review"),
    output: str = typer.Option(
        "llemur_prompt.txt", "--output", help="File to dump prompt for review"
    ),
):
    typer.echo("Executing command 'cr'")
    """
    Automated code review.
    Scans git diffs, prepares a prompt, and either sends it to an LLM for review or dumps it to a file.
    """

    console.print(f"[bold yellow]Prompt and diff dumped to {output} for review.[/bold yellow]")
    try:
        # Step 1: Get the git diff
        diff = subprocess.run(["git", "diff"], capture_output=True, text=True).stdout

        if not diff:
            console.print("[bold red]No changes to review![/bold red]")
            return

        # Get the filenames involved in the diff
        files_changed = subprocess.run(
            ["git", "diff", "--name-only"], capture_output=True, text=True
        ).stdout.splitlines()

        # Collect relevant context for the changed files
        file_contexts = []
        for filename in files_changed:
            # Get full context from file (adjust this as needed)
            # file_context = subprocess.run(["git", "show", f"HEAD:{filename}"], capture_output=True, text=True).stdout
            context_lines = get_context_lines(
                diff, filename, before=20, after=20
            )  # Adjust for real context extraction
            file_contexts.append(f"File: {filename}\n{context_lines}")

        # Step 2: Prepare the prompt
        full_context = "\n\n".join(file_contexts)
        prompt = (
            "This is a code review task. "
            "Please review the following code changes for potential issues, suggest improvements, "
            "and highlight any security vulnerabilities or performance optimizations:\n\n"
            f"Changes:\n{diff}\n\nFull Context:\n{full_context}"
        )

        if send:
            # Step 3: Send to LLM (OpenAI) if --send flag is used
            console.print("\n[bold green]LLM Code Review:[/bold green]")
        else:
            # Step 4: Dump the prompt to a file for review if --send is not used
            with open(output, "w") as fh:
                fh.write(prompt)

            console.print(
                f"[bold yellow]Prompt and diff dumped to {output} for review.[/bold yellow]"
            )

    except Exception as e:
        console.print(f"[bold red]Error during code review: {e}[/bold red]")


def get_context_lines(diff, filename, before=20, after=20):
    """
    Gets lines of context before and after changes in a diff.
    Uses the git diff output to extract the changed line numbers and
    fetches context lines from the file for those changes.

    Args:
        diff (str): The diff output for the repository.
        filename (str): The file to extract context from.
        before (int): Number of lines of context to include before the change.
        after (int): Number of lines of context to include after the change.

    Returns:
        str: A string containing the diff with additional context lines.
    """
    # Step 1: Parse the diff to find changes in the specific file
    file_diff = extract_file_diff(diff, filename)
    if not file_diff:
        return f"No changes found for {filename}"

    # Step 2: Extract the changed line numbers
    line_changes = extract_line_numbers(file_diff)

    # Step 3: Get the context for each line change
    context_lines = []
    for start_line, num_lines in line_changes:
        # The line range we're interested in
        start_context = max(1, start_line - before)
        end_context = start_line + num_lines + after

        # Step 4: Use git show to get the file content at a specific commit
        file_content = get_file_content(filename, start_context, end_context)

        # Step 5: Add this section to the context
        context_lines.append(f"Context for lines {start_context}-{end_context}:\n{file_content}")

    return "\n\n".join(context_lines)


def extract_file_diff(diff, filename):
    """
    Extract the section of the diff that corresponds to the given file.

    Args:
        diff (str): The full diff output.
        filename (str): The name of the file to extract the diff for.

    Returns:
        str: The diff section for the given file.
    """
    in_file = False
    file_diff = []

    # Process diff line by line
    for line in diff.splitlines():
        # Start of a new file diff section
        if line.startswith("diff --git") and filename in line:
            in_file = True
        elif line.startswith("diff --git") and in_file:
            # End of the current file diff section
            break
        elif in_file:
            file_diff.append(line)

    return "\n".join(file_diff)


def extract_line_numbers(file_diff):
    """
    Extracts the changed line numbers from a diff.

    Args:
        file_diff (str): The diff section for a specific file.

    Returns:
        list: A list of tuples, where each tuple contains the starting line and
              the number of lines changed.
    """
    line_changes = []

    # Parse lines that start with @@ (which indicate the line numbers)
    for line in file_diff.splitlines():
        if line.startswith("@@"):
            # Line format example: @@ -7,6 +7,7 @@
            parts = line.split()
            new_file_section = parts[2]  # Example: "+7,7"

            # Extract the start line and number of lines changed
            if "," in new_file_section:
                start_line, num_lines = new_file_section[1:].split(",")
                start_line, num_lines = int(start_line), int(num_lines)
            else:
                start_line = int(new_file_section[1:])
                num_lines = 1

            line_changes.append((start_line, num_lines))

    return line_changes


def get_file_content(filename, start_line, end_line):
    """
    Get the content of a file for a specific range of lines using git show.

    Args:
        filename (str): The file to get content from.
        start_line (int): The starting line number.
        end_line (int): The ending line number.

    Returns:
        str: The file content for the specified range of lines.
    """
    # Use sed to extract specific lines from the file
    cmd = f"sed -n '{start_line},{end_line}p' {filename}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()
