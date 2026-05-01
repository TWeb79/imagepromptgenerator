# Instagram Photo Generator

Generate Instagram-worthy photos using AI. Provide a topic and the tool creates beautiful, aesthetic images optimized for Instagram.

## Overview

The Instagram Photo Generator is a Python CLI tool that generates Instagram-worthy photos based on user-provided topics. It combines LLM-powered prompt generation (via Ollama) with AI image synthesis (via Stable Diffusion) to create professional-quality, Instagram-style images.

## Features

- **Topic-based generation**: Enter any topic (coffee, travel, fitness, food, fashion, etc.)
- **LLM-powered prompt generation**: Uses Ollama to create creative, Instagram-worthy photo prompts
- **AI image generation**: Leverages Stable Diffusion Web UI for high-quality image output
- **Customizable settings**: Adjust output folder and diffusion steps
- **Prompt persistence**: Generated prompts are saved and categorized by topic
- **Legacy format migration**: Automatically migrates old prompt data formats

## Architecture

For detailed system architecture, see [ARCHITECTURE.md](ARCHITECTURE.md).

The system consists of three main components:
1. **Prompt Generator** (Ollama + LLM) — Creates Instagram-style prompts
2. **Image Generator** (Stable Diffusion) — Synthesizes images from prompts
3. **Output Manager** — Saves images and manages prompts

## Requirements

### Software Prerequisites

- **Python 3.8+**
- **[Ollama](https://ollama.ai/)** running locally (port 11434)
  - Model: `llama2-uncensored:7b` (or compatible)
- **[Stable Diffusion Web UI](https://github.com/AUTOMATIC1111/stable-diffusion-webui)** (port 7860)
  - Ensure the API is enabled

### Python Dependencies

```bash
pip install requests
```

## Installation

### Setup Ollama

```bash
ollama serve
# In a separate terminal, pull the model if needed:
ollama run llama2-uncensored
```

### Setup Stable Diffusion Web UI

Follow the official guide: https://github.com/AUTOMATIC1111/stable-diffusion-webui

Ensure it's running with API enabled on port 7860.

### Clone and Run

```bash
git clone <repository-url>
cd 39-ImageGenerator
pip install requests
```

## Usage

### Basic Usage

```bash
python3 app.py "coffee"
```

This will:
1. Generate an Instagram-style prompt for the topic
2. Create an image using Stable Diffusion
3. Save the image to `generated_images/instagram_coffee.png`

### Command Line Options

```
positional arguments:
  topic                 The photo topic (e.g., "coffee", "travel", "fitness")

optional arguments:
  -h, --help            Show help message
  -o, --output FOLDER   Output folder (default: generated_images)
  -s, --steps STEPS     Diffusion steps (default: 20, range: 1-100)
```

### Examples

```bash
# Coffee/lifestyle photo
python3 app.py "coffee"

# Custom output folder
python3 app.py "coffee" -o my_photos

# Higher quality (more diffusion steps)
python3 app.py "travel" -s 30

# Various topics
python3 app.py "fitness"
python3 app.py "food"
python3 app.py "fashion"
```

## How It Works

1. **Topic Processing**: CLI parses the topic and options
2. **Prompt Generation**: 
   - Tests Ollama connectivity
   - Prompts LLM to create an Instagram-style description
   - Falls back to built-in template if Ollama is unavailable
3. **Image Generation**: 
   - Sends prompt to Stable Diffusion Web UI
   - Waits for image synthesis
   - Receives base64-encoded PNG
4. **Output**: 
   - Decodes base64 image
   - Saves as PNG in specified output folder
   - Stores prompt in `generated_prompts.json`

## Project Structure

```
39-ImageGenerator/
├── app.py                      # Main application (CLI orchestration)
├── PROMPT_Instructions.md      # Prompt engineering guidelines
├── ARCHITECTURE.md             # System architecture documentation
├── RULES_coding.md             # Coding standards and best practices
├── README.md                   # This file
├── generated_images/           # Output directory (gitignored)
│   └── instagram_*.png        # Generated images
├── generated_prompts.json      # Saved prompts by topic (gitignored)
├── .gitignore                   # Git ignore rules
└── requirements.txt            # Python dependencies (optional)
```

## Prompt Generation

The tool uses specialized Instagram-style prompt generation guidelines from `PROMPT_Instructions.md`. Generated prompts include:

- **Smartphone/iPhone aesthetic** — Mobile photography style
- **Warm color tones** — Signature Instagram look
- **Shallow depth of field** — Professional bokeh effect
- **Lifestyle context** — Relatable, candid moments
- **Golden hour lighting** — Warm, inviting atmosphere

### Example Generated Prompt

For topic "coffee":
```
artisan latte with heart foam art on rustic wooden table, cozy coffee shop with warm golden hour light streaming through window, exposed brick wall background, smartphone photography, iPhone 15 Pro Max, shallow depth of field, warm color tones, lifestyle photography, Instagram-worthy, highly detailed foam art, steam rising, morning vibes, 8K UHD
```

## Configuration

### Environment Variables

The application uses local defaults. No environment variables are **required**, but you may override:

- `OLLAMA_URL`: Override Ollama endpoint (default: `http://127.0.0.1:11434`)
- `SD_WEBUI_URL`: Override Stable Diffusion endpoint (default: `http://127.0.0.1:7860`)

### Files

- `generated_prompts.json` — Saved prompts organized by topic (automatically managed)
- `config.json` — Optional custom configuration (gitignored)

## Troubleshooting

### Ollama Connection Error

```bash
Error connecting to Ollama: Connection refused
```

**Solution:**
```bash
ollama serve
```

Verify accessibility:
```bash
curl http://127.0.0.1:11434/api/tags
```

### Stable Diffusion Connection Error

```bash
Request to stable diffusion API failed: Connection refused
```

**Solution:**
1. Ensure Stable Diffusion Web UI is running
2. Verify the API is enabled (check Web UI settings)
3. Confirm it's on port 7860

### Empty/Blank Images

If generated images are blank or corrupted:
- Try increasing diffusion steps: `-s 30`
- Check if the prompt is valid (too short or malformed)
- Ensure Stable Diffusion model is properly loaded

### Missing Dependencies

```bash
pip install requests
```

## Development

### Coding Standards

Follow the guidelines in [RULES_coding.md](RULES_coding.md).

Key practices:
- Type hints for all function signatures
- Google-style docstrings
- Maximum 100 character line length
- Functions should be 20 lines or less (when practical)
- Use specific exception types, not bare `except:`

### Running Tests

If tests exist:
```bash
python3 -m pytest tests/ -v
```

### Linting

```bash
ruff check app.py
black app.py --check
mypy app.py
```

### Manual Testing

```bash
# Quick test
python3 app.py "test" -s 1  # Use 1 step for fast testing
```

## API Reference

### Ollama API

- **Endpoint**: `POST http://127.0.0.1:11434/api/generate`
- **Model**: `llama2-uncensored:7b`
- **Timeout**: 120 seconds

### Stable Diffusion API

- **Endpoint**: `POST http://127.0.0.1:7860/sdapi/v1/txt2img`
- **Method**: POST
- **Request**: JSON with `prompt` (string) and `steps` (int)
- **Response**: JSON with `images` array (base64-encoded PNGs)

## Limitations

- Requires local Ollama and Stable Diffusion Web UI instances
- No batch generation (one topic per run)
- No custom negative prompts
- No model selection (uses default SD model)
- Images may vary in quality based on topic and prompt

## Future Enhancements

See [ARCHITECTURE.md](ARCHITECTURE.md#future-enhancements) for planned features.

## Contributing

1. Follow the coding standards in `RULES_coding.md`
2. Add tests for new functionality
3. Update documentation as needed
4. Ensure all linting passes

## Troubleshooting Checklist

- [ ] Ollama is running: `ollama serve`
- [ ] Stable Diffusion Web UI is running on port 7860
- [ ] Python dependencies installed: `pip install requests`
- [ ] Topic is not empty
- [ ] Output folder is writable
- [ ] Sufficient disk space for generated images

## License

MIT License

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review `ARCHITECTURE.md` for system details
3. Review `PROMPT_Instructions.md` for prompt guidelines# imagepromptgenerator
