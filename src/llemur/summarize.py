import ast
import os
import tokenize
from io import StringIO
from pathlib import Path

import typer

summarize_cli = typer.Typer(no_args_is_help=True)

EXCLUDED_DIRS = {"node_modules", "__pycache__", ".git", "dist", "build"}  # Directories to exclude


def summarize_file(file_path: str) -> str:
    """
    Reads the content of a code file and returns a summarized version.

    Args:
        file_path (str): Path to the code file.

    Returns:
        str: Summarized code.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            code = file.read()
        # Use the compress_code function to summarize the code
        summarized_code = compress_code(code)
        return summarized_code
    except Exception as e:
        return f"Error summarizing {file_path}: {e}"


def summarize(
    directory: str = typer.Option(".", "--dir", help="Specify the root directory to summarize"),
    output: str = typer.Option(
        "project_summary.txt", "--output", help="File to dump project summary"
    ),
):
    """
    Summarize all Python, Rust, and TypeScript/JavaScript files under the given directory.
    The summarized content will be written to the specified output file.
    """
    supported_extensions = [".py", ".rs", ".ts", ".js"]
    project_summary = []

    # Walk the directory and summarize relevant files
    for root, dirs, files in os.walk(directory):
        # Exclude directories from scanning
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

        for file in files:
            if any(file.endswith(ext) for ext in supported_extensions):
                file_path = Path(root) / file
                typer.echo(f"Summarizing {file_path}")
                summary = summarize_file(str(file_path))
                project_summary.append(f"File: {file_path}\n{summary}\n{'=' * 40}\n")

    # Write the summary to the output file
    try:
        with open(output, "w", encoding="utf-8") as summary_file:
            summary_file.write("\n".join(project_summary))
        typer.echo(f"Project summary written to {output}")
    except Exception as e:
        typer.echo(f"Error writing to {output}: {e}")


def compress_code(code: str) -> str:
    """
    Compress the code by summarizing, tokenizing, and removing unnecessary parts.

    Args:
        code (str): The code to compress.

    Returns:
        str: The compressed version of the code.
    """
    # Step 1: Remove unnecessary elements (comments, docstrings, etc.)
    cleaned_code = tokenize_code(code)

    # Step 2: Use AST to summarize important elements like functions and classes
    summarized_code = summarize_code_with_ast(cleaned_code)

    return summarized_code


def tokenize_code(code: str) -> str:
    """
    Tokenize the code, removing unnecessary elements like comments and docstrings
    while preserving the critical parts of the code.

    Args:
        code (str): The source code to tokenize.

    Returns:
        str: The tokenized version of the code without unnecessary elements.
    """
    io_obj = StringIO(code)
    output = []

    prev_toktype = tokenize.INDENT
    last_lineno = -1
    last_col = 0
    tokgen = tokenize.generate_tokens(io_obj.readline)

    for tok_type, tok_string, (srow, scol), (erow, ecol), _ in tokgen:
        # Skip comments
        if tok_type == tokenize.COMMENT:
            continue

        # Skip docstrings (detected as STRING tokens that occur at the beginning of functions or classes)
        if tok_type == tokenize.STRING and prev_toktype == tokenize.INDENT:
            continue

        # Add meaningful tokens to the output
        if srow > last_lineno:
            last_col = 0
        if scol > last_col:
            output.append(" " * (scol - last_col))
        output.append(tok_string)

        prev_toktype = tok_type
        last_lineno = erow
        last_col = ecol

    # Return the tokenized code as a string
    return "".join(output)


def remove_comments_and_docstrings(code: str) -> str:
    """
    Removes comments and docstrings from the provided code.

    Args:
        code (str): The source code to clean.

    Returns:
        str: The code without comments and docstrings.
    """
    import tokenize
    from io import StringIO

    io_obj = StringIO(code)
    out = []
    prev_toktype = tokenize.INDENT
    last_lineno = -1
    last_col = 0

    tokgen = tokenize.generate_tokens(io_obj.readline)
    for tok_type, tok_string, (srow, scol), (erow, ecol), _ in tokgen:
        if tok_type == tokenize.COMMENT:
            continue
        if tok_type == tokenize.STRING:
            if prev_toktype == tokenize.INDENT:
                continue

        if srow > last_lineno:
            last_col = 0
        if scol > last_col:
            out.append(" " * (scol - last_col))
        out.append(tok_string)
        prev_toktype = tok_type
        last_lineno = erow
        last_col = ecol

    return "".join(out)


def summarize_code_with_ast(code: str) -> str:
    """
    Summarizes the code by generating a simple Abstract Syntax Tree (AST) structure
    and summarizing functions and class structures.

    Args:
        code (str): The source code to summarize.

    Returns:
        str: A summarized version of the code.
    """
    import ast

    try:
        tree = ast.parse(code)
        summarizer = CodeSummarizer()
        summarizer.visit(tree)
        return summarizer.get_summary()
    except SyntaxError as e:
        return f"Error in parsing code: {e}"


class CodeSummarizer(ast.NodeVisitor):
    """
    AST NodeVisitor to summarize the code structure.
    Summarizes function and class definitions with their names and arguments,
    and selectively includes key elements from function bodies.
    """

    def __init__(self):
        self.summary = []

    def visit_FunctionDef(self, node):
        # Summarize function name and arguments
        args = [arg.arg for arg in node.args.args]
        func_summary = f"Function: {node.name}({', '.join(args)})"

        # Add selected elements from the function body
        func_body_summary = self.summarize_function_body(node.body)
        if func_body_summary:
            func_summary += f"\n  Body: {func_body_summary}"

        self.summary.append(func_summary)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        # Summarize class name
        class_summary = f"Class: {node.name}"
        self.summary.append(class_summary)
        self.generic_visit(node)

    def summarize_function_body(self, body):
        """
        Summarize key parts of the function body, extracting only important statements.

        Args:
            body (list): The list of AST nodes representing the function body.

        Returns:
            str: A summarized version of the function body.
        """
        important_lines = []

        for stmt in body:
            if isinstance(stmt, ast.Assign):
                # Summarize assignment statements
                targets = [self.get_name(t) for t in stmt.targets]
                value = self.get_name(stmt.value)
                important_lines.append(f"{', '.join(targets)} = {value}")
            elif isinstance(stmt, ast.If):
                # Summarize if statements
                test = self.get_name(stmt.test)
                important_lines.append(f"if {test}: ...")
            elif isinstance(stmt, ast.For):
                # Summarize for loops
                target = self.get_name(stmt.target)
                iter_ = self.get_name(stmt.iter)
                important_lines.append(f"for {target} in {iter_}: ...")
            elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                # Summarize function calls
                func_call = self.get_name(stmt.value.func)
                args = [self.get_name(arg) for arg in stmt.value.args]
                important_lines.append(f"{func_call}({', '.join(args)})")
            elif isinstance(stmt, ast.Return):
                # Summarize return statements
                return_value = self.get_name(stmt.value)
                important_lines.append(f"return {return_value}")

        return " | ".join(important_lines)

    def get_name(self, node):
        """
        Helper function to extract names from AST nodes.
        Handles different types of nodes to return a readable name.

        Args:
            node (ast.AST): The AST node to extract a name from.

        Returns:
            str: The name extracted from the node.
        """
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self.get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Call):
            return self.get_name(node.func)
        elif isinstance(node, ast.Constant):
            return str(node.value)
        elif isinstance(node, ast.BinOp):
            return f"{self.get_name(node.left)} {self.get_operator(node.op)} {self.get_name(node.right)}"
        return "..."

    def get_operator(self, op):
        """
        Extracts operator symbols from AST operators.
        """
        return {
            ast.Add: "+",
            ast.Sub: "-",
            ast.Mult: "*",
            ast.Div: "/",
        }.get(type(op), "?")

    def get_summary(self):
        """
        Returns the full summary of the code as a string.
        """
        return "\n".join(self.summary)
