# Architecture Documentation

## Overview

The Instagram Photo Generator is a Python CLI tool that generates Instagram-worthy photos based on user-provided topics. It combines LLM-powered prompt generation (via Ollama) with AI image synthesis (via Stable Diffusion Web UI) following a clean, three-tier architecture.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         User Input                                  │
│                      (Topic: "coffee")                              │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       CLI Layer (app.py)                            │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Argument Parser                         │   │
│  │  - Validates topic, output folder, steps                    │   │
│  │  - Handles CLI flags (-o, -s, --help)                      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                 Workflow Orchestration                      │   │
│  │  - Coordinates prompt generation → image synthesis → output  │   │
│  │  - Manages error handling and user feedback                  │   │
│  │  - Persists generated prompts (generated_prompts.json)       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                               │
               ┌───────────────┴───────────────┐
               ▼                               ▼
┌─────────────────────────┐    ┌─────────────────────────────┐
│  Prompt Service         │    │   Image Generation Service   │
│                         │    │                             │
│  get_instagram_prompt() │    │    generate_image()         │
│                         │    │                             │
│  - Connects to Ollama   │    │  - Connects to SD WebUI     │
│  - Sends topic          │    │  - Sends prompt & steps     │
│  - Receives prompt      │    │  - Receives image (base64)  │
│                         │    │                             │
└─────────────────────────┘    └─────────────────────────────┘
               │                               │
               ▼                               ▼
┌─────────────────────────┐    ┌─────────────────────────────┐
│      Ollama API         │    │  Stable Diffusion API        │
│   (localhost:11434)     │    │     (localhost:7860)         │
│                         │    │                             │
│  Model: llama2-uncensored│   │  Endpoint: /sdapi/v1/txt2img │
│  Timeout: 120s          │    │  Timeout: 120s               │
└─────────────────────────┘    └─────────────────────────────┘
               │                               │
               ▼                               ▼
┌─────────────────────────┐    ┌─────────────────────────────┐
│     Generated Prompt    │    │      Base64 Image Data       │
│    (Instagram-style)    │    │                             │
└─────────────────────────┘    └─────────────────────────────┘
               │                               │
               └───────────────┬───────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      Output Manager                                 │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                   save_image()                               │   │
│  │  - Validates & sanitizes filename                             │   │
│  │  - Creates output directory (if needed)                       │   │
│  │  - Decodes base64 → PNG                                       │   │
│  │  - Writes to disk                                             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                  Prompt Persistence                          │   │
│  │  - load_prompts(): Loads & migrates legacy format            │   │
│  │  - add_prompt_to_topic(): Appends to topic                    │   │
│  │  - save_prompts(): Persists to JSON file                     │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     Output: instagram_*.png                          │
└─────────────────────────────────────────────────────────────────────┘
```

## Components

### 1. CLI Layer (app.py)

The entry point provides command-line interface functionality.

**Responsibilities:**
- Command-line argument parsing
- Input validation
- Workflow orchestration
- Error handling and user feedback

**Key Functions:**

#### `main()` / `if __name__ == "__main__"`
- **Input**: Command-line arguments
- **Process**: 
  - Parses topic, output folder, steps
  - Orchestrates prompt generation, image creation, output
- **Output**: Success/failure with user feedback

#### `get_instagram_prompt(topic: str) -> str`
- **Input**: Topic string (e.g., "coffee", "travel")
- **Process**: 
  - Tests Ollama connectivity with simple probe
  - Requests Instagram-style prompt from LLM
  - Falls back to built-in template on failure
- **Output**: Instagram-ready prompt string

#### `generate_image(prompt: str, url: str, steps: int) -> Optional[str]`
- **Input**: 
  - `prompt`: Generated Instagram prompt
  - `url`: Stable Diffusion API endpoint
  - `steps`: Diffusion iterations
- **Process**: 
  - POSTs to `/sdapi/v1/txt2img`
  - Validates and extracts base64 image
- **Output**: Base64-encoded PNG data or `None`

#### `save_image(image_data: str, filename: str, folder: str) -> None`
- **Input**:
  - `image_data`: Base64-encoded PNG
  - `filename`: Output filename
  - `folder`: Output directory
- **Process**:
  - Creates directory if needed
  - Decodes base64
  - Writes binary file
- **Output**: PNG file on disk

#### Prompt Persistence Functions

- `load_prompts() -> Dict[str, List[str]]`: Loads `generated_prompts.json`, migrates legacy format
- `add_prompt_to_topic(topic, prompt, prompts)`: Appends prompt to topic category
- `save_prompts(prompts) -> bool`: Writes prompts to JSON file

### 2. External Services

#### Ollama (Port 11434)
- **Purpose**: LLM-powered prompt generation
- **Model**: `llama2-uncensored:7b`
- **API**: `POST /api/generate`
- **Timeout**: 120 seconds
- **Fallback**: Built-in Instagram prompt template

#### Stable Diffusion Web UI (Port 7860)
- **Purpose**: AI image synthesis
- **Endpoint**: `POST /sdapi/v1/txt2img`
- **Timeout**: 120 seconds
- **Fallback**: None (fails gracefully with error message)

## Data Flow

```
User Input
    │
    ▼
[CLI Layer] ──→ validate & parse
    │
    ▼
[Prompt Generation] ──┐
    │ (Ollama API)     │
    ▼                   │ (if fails)
[Generated Prompt] ◄───┘
    │
    ▼
[Image Generation] ─────┐
    │ (SD WebUI API)     │
    ▼                    │ (if fails)
[Base64 Image] ◄─────────┘
    │
    ▼
[Output Manager] ──→ decode → save PNG
    │
    ▼
[Prompt Persistence] ──→ update JSON
    │
    ▼
Success / Error
```

## Error Handling

| Error Condition | Handling Strategy | User Feedback |
|----------------|-------------------|---------------|
| Empty topic | Early validation, exit(1) | "Error: Topic cannot be empty" |
| Ollama unavailable | Fallback prompt generation | "Using fallback Instagram prompt" |
| Ollama API error | Fallback prompt generation | "Error connecting to Ollama" |
| SD WebUI unavailable | Graceful failure, exit(1) | "Request to stable diffusion API failed" |
| Invalid API response | Graceful handling with error | "Unexpected response format" |
| File I/O errors | Return error code (save_prompts) | "Error saving prompts file" |

## Configuration

### Command Line Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `topic` | string | required | Photo subject/theme |
| `-o, --output` | string | `generated_images` | Output directory |
| `-s, --steps` | int | 20 | Diffusion steps (1-100) |

### API Endpoints

| Service | URL | Purpose |
|---------|-----|---------|
| Ollama | `http://127.0.0.1:11434` | LLM prompt generation |
| Stable Diffusion | `http://127.0.0.1:7860` | Image synthesis |

## File Structure

```
39-ImageGenerator/
├── app.py                      # Main CLI application
├── PROMPT_Instructions.md      # Prompt engineering guides
├── ARCHITECTURE.md             # This file
├── RULES_coding.md             # Coding standards
├── README.md                   # User documentation
├── generated_images/           # Output directory (gitignored)
│   └── instagram_<topic>.png   # Generated images
├── generated_prompts.json      # Saved prompts (gitignored)
├── .gitignore                   # Git ignore rules
└── requirements.txt            # Dependencies (optional)
```

## Dependencies

| Package | Purpose | Required |
|---------|---------|----------|
| `requests` | HTTP client for API calls | Yes |
| Python 3.8+ | Runtime environment | Yes |
| Ollama | LLM service | External |
| Stable Diffusion | Image generation | External |

## Security Considerations

- **Local-only**: All API calls are to localhost (127.0.0.1)
- **No external network**: No internet access required
- **No secrets**: No authentication tokens needed
- **Sanitized filenames**: User input sanitized before file operations
- **No sensitive data**: No credentials or keys stored

## Future Enhancements

See [ARCHITECTURE.md](ARCHITECTURE.md#future-enhancements) for details.

1. **Batch generation**: Process multiple topics in one run
2. **Prompt templates**: Customizable prompt structures
3. **Negative prompts**: SD WebUI negative prompt support
4. **Image preview**: Display before saving
5. **Multiple topics**: Single command for multiple subjects
6. **Custom models**: Support different Ollama/SD models
7. **Progress indication**: Show generation progress
8. **Async operations**: Parallel prompt & image generation
9. **Configuration file**: YAML/JSON config for settings
10. **Plugin system**: Extensible service architecture