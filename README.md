# LLeMur
A cute animal that hangs out in the LLM jungle, streamlining developer 
workflows by facilitating easy and safe interactions with Large Language 
Models (LLMs) like ChatGPT, Claude, and LLaMA3 from the command line.

## Overview
Llemur is a CLI tool designed to streamline developer workflows by 
integrating with various LLMs for tasks such as code reviews, 
brainstorming, file generation, and more. By allowing seamless 
interactions with LLMs directly from the terminal, Llemur makes it 
easy to integrate AI-powered workflows into any software development 
process.

Llemur also prioritizes safety by ensuring that no code or sensitive 
information is sent to external LLM services unless a specific switch 
is provided, allowing developers to review the prompt and code before 
sending.

## Proposed Features
- Automated Code Review: Review your code diffs with a single command, 
  using LLMs to identify potential issues, improvements, and security 
  vulnerabilities.
- Ctext Management: Easily add or remove code to/from context and 
  manage sessions with multiple LLM platforms.
- LLM Interactions: Interact with various LLMs (e.g., ChatGPT, Claude, 
  LLaMA3, etc.) from the command line.
- Flexible Prompt Management: Use predefined and customizable prompts 
  tailored for development.
- Safe by Default: By default, Llemur dumps prompts to a file for 
  review before sending them to LLMs.
- Integration with Git: Automatically gather git diff information for 
  code reviews.

## License

This project is licensed under the MIT License. See the LICENSE file 
for details.

You can now build on this README by adding more details about commands, configuration, or use cases as your project evolves.