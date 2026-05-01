# Coding Rules and Standards

## Overview
This document defines the coding standards, best practices, and architectural rules for the Instagram Photo Generator project. All code contributions must adhere to these guidelines.

## Table of Contents
1. [Code Style](#code-style)
2. [Python Standards](#python-standards)
3. [Function Design](#function-design)
4. [Error Handling](#error-handling)
5. [API Integration](#api-integration)
6. [Security](#security)
7. [Documentation](#documentation)
8. [Testing](#testing)
9. [File Organization](#file-organization)
10. [Git Practices](#git-practices)

## Code Style

### General Principles
- **Readability over cleverness**: Code should be easily understood by others
- **Consistency**: Follow existing patterns in the codebase
- **DRY (Don't Repeat Yourself)**: Extract reusable logic into functions
- **KISS (Keep It Simple)**: Avoid unnecessary complexity
- **YAGNI (You Aren't Gonna Need It)**: Don't add features that aren't needed

### Python Specific
- Use Python 3.8+ features where appropriate
- Follow PEP 8 style guide
- Line length: max 100 characters (except URLs/docstrings)
- Use spaces, not tabs (4 spaces per indent level)
- Use double quotes for strings (except docstrings which use triple double quotes)
- Use type hints for function signatures

### Naming Conventions
```python
# Functions and variables: snake_case
def get_instagram_prompt(topic):
    pass

# Constants: UPPER_SNAKE_CASE
PROMPTS_FILE = "generated_prompts.json"
MAX_RETRIES = 3

# Classes: PascalCase
class InstagramGenerator:
    pass

# Private functions: _leading_underscore (internal use only)
def _generate_fallback_instagram_prompt(topic):
    pass
```

## Python Standards

### Imports
- Group imports in this order: standard library, third-party, local
- Use absolute imports
- One import per line
- Avoid wildcard imports

```python
# Good
import os
import sys
from typing import Optional

import requests

# Bad
import os, sys
from requests import *
```

### Type Hints
- Use type hints for all function signatures
- Import types from `typing` module when needed

```python
from typing import Optional, Dict, List, Any

def get_instagram_prompt(topic: str) -> str:
    pass

def load_prompts() -> Dict[str, List[str]]:
    pass
```

### Constants
- Define at module level for magic values
- Use descriptive names
- Document their purpose

```python
# Good
OLLAMA_URL = "http://127.0.0.1:11434"
SD_API_URL = "http://127.0.0.1:8141"
DEFAULT_STEPS = 20
PROMPT_TIMEOUT = 120

# Bad
def func():
    url = "http://127.0.0.1:11434"  # magic value
```

## Function Design

### Single Responsibility Principle
Each function should do one thing and do it well.

```python
# Bad: Does too many things
def process_topic(topic: str) -> None:
    prompt = generate_prompt(topic)
    image = generate_image(prompt)
    save_image(image, topic)
    save_prompt(topic, prompt)
    print("Done")

# Good: Separate concerns
def orchestrate_workflow(topic: str, output_dir: str) -> bool:
    prompt = generate_prompt(topic)
    image = generate_image(prompt)
    if image:
        save_image(image, topic, output_dir)
        save_prompt(topic, prompt)
        return True
    return False
```

### Function Length
- Aim for 20 lines or less per function
- Extract helper functions when logic gets complex
- Long functions are acceptable for orchestration or main execution

### Parameters
- Limit function parameters (max 5 preferred)
- Use keyword arguments for optional parameters
- Group related parameters into config dicts or dataclasses if many

```python
# Good
def generate_image(prompt: str, steps: int = 20) -> Optional[str]:
    pass

# Avoid too many parameters
def complex_function(a, b, c, d, e, f, g, h):
    pass  # Hard to understand and use
```

### Return Values
- Be consistent with return types
- Return `None` or raise exceptions for failures (document which)
- Avoid returning magic values (-1, empty strings) for errors

## Error Handling

### Exception Handling
- Use specific exception types, not bare `except:`
- Handle recoverable errors gracefully
- Log or report errors appropriately
- Don't swallow exceptions silently

```python
# Good
try:
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()
except requests.exceptions.Timeout:
    print(f"Timeout connecting to {url}")
    return None
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
    return None

# Bad
try:
    response = requests.post(url)
except:
    pass  # Silent failure
```

### Error Messages
- Be clear and actionable
- Include context (function name, relevant values)
- Don't expose sensitive information

```python
# Good
print(f"Error: Could not connect to Ollama at {url}: {e}")

# Bad
print(f"Error {e}")
```

### Validation
- Validate inputs early (fail fast)
- Check preconditions
- Use assertions for internal invariants

```python
def generate_image(prompt: str, steps: int = 20) -> Optional[str]:
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty")
    if steps < 1 or steps > 100:
        raise ValueError("Steps must be between 1 and 100")
    # ... rest of function
```

## API Integration

### External Services
- Isolate API calls in dedicated functions
- Use timeouts (max 120 seconds for LLM calls)
- Handle connection failures gracefully
- Implement retry logic for transient failures (with backoff)

```python
def call_ollama(prompt: str, timeout: int = 120) -> Optional[str]:
    payload = {
        "model": "llama2-uncensored:7b",
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(url, json=payload, timeout=timeout)
        response.raise_for_status()
        return response.json().get('response')
    except requests.exceptions.Timeout:
        print(f"Timeout after {timeout}s")
        return None
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        return None
```

### Configuration
- Use environment variables for sensitive config
- Keep defaults sensible
- Document all configuration options

### Request/Response Format
- Validate API responses (check for expected keys)
- Handle malformed responses gracefully
- Use constants for API endpoints

## Security

### Sensitive Data
- Never commit secrets (API keys, tokens) to version control
- Use `.gitignore` to exclude config files with secrets
- Use environment variables for secrets

### File Operations
- Validate file paths
- Use `os.makedirs(exist_ok=True)` for directories
- Handle file I/O errors
- Sanitize user input that becomes filenames

```python
# Good - sanitizes filename
safe_name = "".join(c if c.isalnum() else "_" for c in topic)
filename = f"instagram_{safe_name}.png"

# Bad - potential path traversal
filename = f"instagram_{topic}.png"  # topic could be "../../etc/passwd"
```

### Network Security
- Prefer HTTPS for external APIs
- Validate SSL certificates
- Don't disable certificate verification

## Documentation

### Code Comments
- Explain **why**, not **what** (the code should be self-explanatory)
- Document complex algorithms or decisions
- Avoid redundant comments

```python
# Bad: States the obvious
x = x + 1  # Increment x by 1

# Good: Explains the why
# Use 120s timeout for LLM to handle complex prompts
timeout = 120
```

### Docstrings
- Use Google-style or NumPy-style docstrings
- Include Args, Returns, Raises sections
- Document public APIs

```python
def get_instagram_prompt(topic: str) -> str:
    """Generate an Instagram-style photo prompt for the given topic.
    
    Uses Ollama to create a creative, Instagram-worthy prompt description.
    Falls back to a built-in template if Ollama is unavailable.
    
    Args:
        topic: The photo subject/theme (e.g., "coffee", "travel", "fitness")
    
    Returns:
        A detailed photo prompt string suitable for Stable Diffusion
    """
    pass
```

### Module/File Documentation
- Include a brief description at the top
- List key functions and their purposes
- Note any external dependencies

## Testing

### Test Coverage
- Write tests for core functionality
- Test edge cases and error conditions
- Mock external dependencies (APIs, file I/O)

### Test Organization
- Place tests in `tests/` directory
- Mirror source code structure
- Use descriptive test names

```python
# Good
def test_generate_instagram_prompt_with_topic():
    pass

def test_generate_image_handles_api_timeout():
    pass

# Bad
def test_1():
    pass

def test_stuff():
    pass
```

### Test Independence
- Tests should not depend on each other
- Use fixtures for common setup
- Clean up after each test

## File Organization

### Directory Structure
```
project/
├── app.py                 # Main application entry
├── README.md              # User documentation
├── ARCHITECTURE.md        # Architecture docs
├── RULES_coding.md        # Coding standards (this file)
├── PROMPT_Instructions.md # Prompt guidelines
├── requirements.txt       # Dependencies
├── .gitignore             # Git ignore rules
├── tests/                 # Test directory
│   ├── test_app.py
│   └── ...
└── generated_images/      # Output directory (gitignored)
```

### File Responsibilities
- **app.py**: Main CLI application, argument parsing, workflow orchestration
- **README.md**: User-facing documentation (installation, usage, examples)
- **ARCHITECTURE.md**: System design, components, data flow
- **RULES_coding.md**: Coding standards and best practices
- **PROMPT_Instructions.md**: Prompt engineering guidelines

## Git Practices

### Commit Messages
- Use conventional commit format
- Write in present tense
- Keep subject under 72 characters
- Include body for complex changes

```
feat: add batch generation mode

- Add --batch flag to process multiple topics
- Support reading topics from file
- Generate variations with different parameters
```

### Branching
- Use feature branches for new work
- Keep branches focused and short-lived
- Rebase on main before merging

### Pull Requests
- Include description of changes
- Reference related issues
- Update documentation as needed
- Ensure tests pass

### Pre-commit
- Run linter (ruff/black)
- Run type checker (mypy/pyright)
- Run tests
- No debug prints in production code

## Linting and Formatting

### Tools
- **ruff**: Linter (replace flake8/pylint)
- **black**: Code formatter
- **isort**: Import sorting
- **mypy**: Type checker

### Configuration
Add `.ruff.toml`, `pyproject.toml` with project-specific rules.

## Dependencies

### Adding Dependencies
- Minimize external dependencies
- Prefer standard library when possible
- Document why each dependency is needed
- Pin versions in requirements.txt

### Virtual Environments
- Always use a virtual environment
- Don't commit venv directory
- Use `requirements.txt` for reproducibility

## Logging

### Log Levels
- Use appropriate log levels (DEBUG, INFO, WARNING, ERROR)
- Don't use print() for production logging
- Log important events and errors

### User Feedback
- Print progress for long operations
- Show errors clearly to users
- Provide actionable error messages

## Performance

### Bottlenecks
- Profile before optimizing
- Identify true bottlenecks
- Optimize algorithms, then code

### Caching
- Cache expensive computations
- Cache API responses when appropriate
- Consider file-based caching for generated prompts

### Memory
- Process large files in chunks
- Don't load entire files into memory
- Clean up resources (close files, db connections)

## Review Checklist

Before committing code:
- [ ] Follows PEP 8 and project style
- [ ] Has type hints
- [ ] Includes docstrings for public functions
- [ ] Handles errors appropriately
- [ ] Validates inputs
- [ ] No print() statements (except CLI feedback)
- [ ] No TODO comments (or tracked separately)
- [ ] No commented-out code
- [ ] Passes linting
- [ ] Passes type checking
- [ ] Has tests for new functionality
- [ ] Updates documentation if needed
- [ ] Gitignore excludes generated files