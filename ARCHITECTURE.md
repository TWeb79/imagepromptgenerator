# Architecture Documentation

## Overview

The Instagram Photo Generator is a Python CLI tool that generates Instagram-worthy photos based on user-provided topics. It combines LLM-powered prompt generation (via Ollama) with AI image synthesis (via Stable Diffusion) following a clean, three-tier architecture.

The system supports **two image generation modes**:
1. **Local Mode** — Uses a local Stable Diffusion Web UI installation
2. **Online Mode** — Uses the ModelsLab cloud API (no local installation required)

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
│  │  - Handles CLI flags (-o, -s, --online, --service)         │   │
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
│  - Connects to Ollama   │    │  - Local SD WebUI or        │
│  - Sends topic          │    │    Online ModelsLab API     │
│  - Receives prompt      │    │  - Sends prompt & steps     │
│                         │    │  - Receives image (base64)  │
└─────────────────────────┘    └─────────────────────────────┘
               │                               │
               │                               │
               │                               │
   ┌───────────┴───────────┐    ┌──────────────┴───────────────┐
   ▼                       ▼    ▼                               ▼
┌─────────────────┐    ┌─────────────────┐         ┌─────────────────────┐
│     Ollama      │    │ Local SD WebUI  │         │  ModelsLab Online   │
│   (localhost)   │    │   (localhost)   │         │      API            │
│                 │    │                 │         │                     │
│  Model:         │    │  Endpoint:      │         │  Endpoint:          │
│  llama2-uncensored│   │  /sdapi/v1/     │         │  modelslab.com/     │
│  Timeout: 120s  │    │    txt2img      │         │    api/v6/          │
│                 │    │  Timeout: 120s  │         │  Timeout: 120s      │
└─────────────────┘    └─────────────────┘         └─────────────────────┘
               │                       │                         │
               ▼                       ▼                         ▼
┌─────────────────────────┐    ┌─────────────────────────────┐
│     Generated Prompt    │    │    Base64 Image Data        │
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

## Image Generation Services

The system supports two interchangeable image generation services:

### 1. Local Stable Diffusion Web UI
- **URL**: `http://127.0.0.1:7860/sdapi/v1/txt2img`
- **Mode**: Local (requires installation)
- **Requirements**: 
  - Automatic1111 Stable Diffusion Web UI running
  - API enabled in Web UI settings
  - GPU recommended but not required
- **Pros**: Free, private, no network calls, unlimited generations
- **Cons**: Requires installation and setup, needs GPU for speed
- **CLI**: `--service local` (default) or `--service modelslab` to switch

### 2. ModelsLab Online API
- **URL**: `https://modelslab.com/api/v6/images/text2img`
- **Mode**: Cloud-based
- **Requirements**:
  - Free API key from https://modelslab.com/
  - Internet connection
  - API key set via `--api-key` or `SD_API_KEY` environment variable
- **Pros**: No installation, works anywhere, free API key
- **Cons**: Requires internet, rate limits, prompts sent to third-party
- **CLI**: `--online` flag or `--service modelslab --api-key YOUR_KEY`

## Service Abstraction

```python
class ImageGenerationService(Protocol):
    def generate(self, prompt: str, steps: int) -> Optional[str]:
        ...

class LocalStableDiffusionService(ImageGenerationService):
    # Uses local SD Web UI
    ...

class ModelsLabOnlineService(ImageGenerationService):
    # Uses ModelsLab cloud API
    ...
```

The application uses a factory pattern to create the appropriate service:

```python
def create_service(
    service_type: str,
    api_key: Optional[str] = None,
    url: str = SD_WEBUI_URL
) -> ImageGenerationService:
    if service_type == "local":
        return LocalStableDiffusionService(url)
    elif service_type == "modelslab":
        return ModelsLabOnlineService(api_key)
```

## Components

### 1. CLI Layer (app.py)

The entry point provides command-line interface functionality.

**Responsibilities:**
- Command-line argument parsing (`parse_arguments()`)
- Service selection and creation (`create_service()`)
- Workflow orchestration
- Error handling and user feedback

**Key Functions:**

#### `parse_arguments() -> argparse.Namespace`
- **Purpose**: Parse CLI arguments
- **Args**: `--topic`, `-o/--output`, `-s/--steps`, `--online`, `--api-key`, `--service`
- **Returns**: Parsed arguments namespace

#### `create_service(service_type, api_key, url) -> ImageGenerationService`
- **Purpose**: Factory function to instantiate the appropriate service
- **Types**: `"local"` or `"modelslab"`
- **Returns**: Service instance implementing `ImageGenerationService`

#### `get_api_key(cli_key) -> Optional[str]`
- **Purpose**: Get API key from CLI, environment, or config file
- **Priority**: CLI > `SD_API_KEY` env var > `config.json`

#### `get_instagram_prompt(topic) -> str`
- **Purpose**: Generate Instagram-style prompt via Ollama or fallback
- **Uses**: `test_ollama_connection()`, `generate_instagram_prompt_from_ollama()`

#### `generate_image(prompt, service, steps) -> Optional[str]`
- **Purpose**: Generate image using the provided service
- **Service**: Any `ImageGenerationService` implementation
- **Returns**: Base64-encoded PNG or `None`

#### `save_image(image_data, filename, folder) -> None`
- **Purpose**: Save decoded PNG to disk
- **Process**: Base64 decode → write file

#### `main()`
- **Purpose**: Orchestrates the complete workflow
- **Flow**: Parse args → create service → generate prompt → generate image → save

### 2. Prompt Service

**Functions:**
- `test_ollama_connection()` — Tests Ollama availability
- `generate_instagram_prompt_from_ollama(topic)` — Requests prompt from LLM
- `_generate_fallback_instagram_prompt(topic)` — Built-in template
- `get_instagram_prompt(topic)` — Main entry point with fallback

### 3. Image Generation Services

#### LocalStableDiffusionService
- POSTs to `/sdapi/v1/txt2img`
- Request: `{"prompt": str, "steps": int}`
- Response: `{"images": ["base64_data"]}`
- Timeout: 120 seconds

#### ModelsLabOnlineService
- POSTs to `https://modelslab.com/api/v6/images/text2img`
- Request: `{"key": str, "model_id": str, "prompt": str, "negative_prompt": str, ...}`
- Response: `{"status": "success", "images": ["base64_data"]}`
- Timeout: 120 seconds
- Steps clamped to 1-50

### 4. External Services

#### Ollama (Port 11434)
- **Purpose**: LLM-powered prompt generation
- **Model**: `llama2-uncensored:7b`
- **API**: `POST /api/generate`
- **Timeout**: 10s (test), 120s (generation)
- **Status**: Required for creative prompts (fallback available)

#### Stable Diffusion Web UI (Port 7860)
- **Purpose**: Local image generation
- **Endpoint**: `POST /sdapi/v1/txt2img`
- **Timeout**: 120 seconds
- **Status**: Required for local mode

#### ModelsLab API
- **Purpose**: Cloud-based image generation
- **Endpoint**: `POST https://modelslab.com/api/v6/images/text2img`
- **Timeout**: 120 seconds
- **Status**: Required for online mode
- **Auth**: Free API key

## Data Flow

### Local Mode
```
User Input
    │
    ▼
[CLI Layer] ──→ parse & validate
    │
    ▼
[Service Selection] ──→ LocalStableDiffusionService
    │
    ▼
[Prompt Generation] ──┐
    │                  │
    ▼                  │
[Ollama API] ──┐      │
    │          │      │
    ▼          │      │
[Generated Prompt] <──┘ (fallback if fail)
    │
    ▼
[Image Generation] ───→ Local SD Web UI
    │
    ▼
[Base64 Image]
    │
    ▼
[Output Manager] ──→ decode → save PNG
    │
    ▼
[Result]
```

### Online Mode
```
User Input
    │
    ▼
[CLI Layer] ──→ parse & validate
    │
    ▼
[Service Selection] ──→ ModelsLabOnlineService
    │                    (verify API key)
    ▼
[Prompt Generation] ──┐
    │                  │
    ▼                  │
[Ollama API] ──┐      │
    │          │      │
    ▼          │      │
[Generated Prompt] <──┘ (fallback if fail)
    │
    ▼
[Image Generation] ───→ ModelsLab API
    │
    ▼
[Base64 Image]
    │
    ▼
[Output Manager] ──→ decode → save PNG
    │
    ▼
[Result]
```

## Error Handling

| Error | Local Mode | Online Mode | User Feedback |
|-------|-----------|-------------|---------------|
| Empty topic | Exit(1) | Exit(1) | "Error: Topic cannot be empty" |
| Ollama unavailable | Fallback prompt | Fallback prompt | "Using fallback Instagram prompt" |
| SD WebUI unavailable | Exit(1) | N/A | "Failed: local service" + suggest online |
| Invalid API key | N/A | Exit(1) | "Error: Invalid API key" |
| Rate limited | N/A | Exit(1) | "Error: Rate limited" |
| No internet | OK | Exit(1) | "Could not connect" + suggest offline |
| Image decode fail | Exit(1) | Exit(1) | "Failed to save image" |

## Configuration

### Command Line Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `topic` | string | required | Photo subject/theme |
| `-o, --output` | string | `generated_images` | Output directory |
| `-s, --steps` | int | 20 | Diffusion steps |
| `--online` | flag | False | Use online service |
| `--api-key` | string | None | ModelsLab API key |
| `--service` | string | `local` | Service type (`local`/`modelslab`) |

### Environment Variables

| Variable | Purpose | Example |
|----------|---------|----------|
| `SD_API_KEY` | ModelsLab API key | `export SD_API_KEY='abc123...'` |
| `SD_SERVICE` | Default service | `export SD_SERVICE='modelslab'` |

### Files

- `config.json` — Optional: `{"api_key": "your_key"}`
- `generated_prompts.json` — Auto-generated prompt cache
- `.gitignore` — Excludes generated files and configs

## File Structure

```
39-ImageGenerator/
├── app.py                      # Main CLI application (703 lines)
├── PROMPT_Instructions.md      # Prompt engineering guides
├── ARCHITECTURE.md             # This file
├── RULES_coding.md             # Coding standards
├── README.md                   # User documentation
├── generated_images/           # Output directory (gitignored)
│   └── instagram_<topic>.png   # Generated images
├── generated_prompts.json      # Saved prompts (gitignored)
├── config.json                 # Optional API key config (gitignored)
└── .gitignore                   # Git ignore rules
```

## Dependencies

| Package | Purpose | Required | Version |
|---------|---------|----------|---------|
| `requests` | HTTP client | Yes | 2.33+ |
| Python | Runtime | Yes | 3.8+ |
| Ollama | Prompt generation | External | Any |
| SD WebUI | Local generation | Optional | Any |
| ModelsLab API | Online generation | Optional | Free tier |

## Security Considerations

### Local Mode
- ✅ All API calls to localhost
- ✅ No external network traffic
- ✅ No sensitive data transmitted
- ✅ No API keys needed
- ✅ Fully offline capable

### Online Mode
- ⚠️ Prompts sent to third-party API
- ⚠️ Requires API key (store securely)
- ⚠️ Internet connection required
- ⚠️ Subject to provider's privacy policy
- ⚠️ Potential rate limits

### Security Practices
- API keys not logged or persisted to prompts file
- Filenames sanitized to prevent path traversal
- HTTPS for all external API calls
- Timeout protection on all requests
- Input validation at all boundaries

## Future Enhancements

See [ARCHITECTURE.md](ARCHITECTURE.md#future-enhancements) for details.
7. **Progress indication**: Show generation progress
8. **Async operations**: Parallel prompt & image generation
9. **Configuration file**: YAML/JSON config for settings
10. **Plugin system**: Extensible service architecture