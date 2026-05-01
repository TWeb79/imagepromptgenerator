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
2. **Image Generator** (SDAPI) — Synthesizes images from prompts
3. **Output Manager** — Saves images and manages prompts

## Requirements

### Software Prerequisites

- **Python 3.8+**
- **[Ollama](https://ollama.ai/)** running locally (port 11434)
  - Model: `llama2-uncensored:7b` (or compatible)
  - Used only for prompt generation
- **One** of the following for image generation:
  - **SDAPI** running locally (port 8141) https://github.com/TWeb79/stablediffusionprovider
  **OR**. 
  - **ModelsLab API key** for online generation (no local installation needed)

### Python Dependencies

```bash
pip install requests
```

## Installation

### Option 1: Local SDAPI (Full Installation)

#### Setup Ollama

```bash
ollama serve
# In a separate terminal, pull the model if needed:
ollama run llama2-uncensored
```

#### Setup SDAPI

Run SDAPI with Stable Diffusion models on port 8141. See [SDAPI.md](SDAPI.md) for setup details.

Then install the Python dependency:

```bash
pip install requests
```

### Option 2: Online Stable Diffusion (Quick Start)

No local installation required! Just get a free API key.

1. **Get a free ModelsLab API key**:
   - Visit: https://modelslab.com/
   - Sign up for a free account
   - Get your API key from the dashboard

2. **Set the API key** (choose one method):

   ```bash
   # Method 1: Environment variable (recommended)
   export SD_API_KEY='your_api_key_here'
   
   # Method 2: Pass via command line
   python3 app.py "coffee" --online --api-key your_api_key_here
   
   # Method 3: Create config.json
   echo '{"api_key": "your_api_key_here"}' > config.json
   ```

3. **Install Python dependency**:

   ```bash
   pip install requests
   ```

## Usage

### Local Mode (Default)

Uses local SDAPI on port 8141:

```bash
python3 app.py "coffee"
```

### Online Mode (No Local Installation)

Uses ModelsLab cloud API:

```bash
python3 app.py "coffee" --online
```

If you've set the `SD_API_KEY` environment variable, it will be used automatically.

### Command Line Options

```
positional arguments:
  topic                 The photo topic (e.g., "coffee", "travel", "fitness")

optional arguments:
  -h, --help            Show help message
  -o, --output FOLDER   Output folder (default: generated_images)
  -s, --steps STEPS     Diffusion steps (default: 20)
  --online              Use online Stable Diffusion (ModelsLab)
  --api-key KEY         ModelsLab API key (or set SD_API_KEY env var)
  --service {local,modelslab}
                        Generation service (default: local)
```

### Examples

#### Local Mode

```bash
# Basic usage
python3 app.py "coffee"

# Custom output folder
python3 app.py "travel" -o my_photos

# More diffusion steps for higher quality
python3 app.py "fitness" -s 30
```

#### Online Mode

```bash
# Using environment variable (recommended)
export SD_API_KEY='your_key_here'
python3 app.py "coffee" --online

# Passing API key directly
python3 app.py "travel" --online --api-key your_key_here

# With custom settings
python3 app.py "food" --online -o my_online_images -s 30
```

#### Switching Between Modes

```bash
# If local SDAPI is running
python3 app.py "fashion"                    # Uses local

# If local installation is not available
python3 app.py "fashion" --online           # Uses online

# Explicitly choose
python3 app.py "fitness" --service local    # Force local
python3 app.py "fitness" --service modelslab  # Force online
```

## How It Works

### Architecture (See ARCHITECTURE.md)

The application supports two image generation backends:

1. **Local SDAPI**
   - Runs on localhost:8141
   - Requires full SD installation via SDAPI
   - Free (aside from compute resources)
   - No network calls outside localhost
   - Best for frequent use with powerful GPU

2. **ModelsLab Online API**
   - Cloud-based Stable Diffusion XL
   - No local installation required
   - Free API key from ModelsLab
   - Requires internet connection
   - Best for quick testing or machines without GPU

### Workflow

```
User Input → CLI Parsing → Service Selection
    │
    ├─[Local Mode]→ Ollama (prompt) → SDAPI (image)
    │
    └─[Online Mode]→ Ollama (prompt) → ModelsLab API (image)
                        │
                        └─[Fallback]→ Built-in template
    │
    └─→ Output: PNG image + saved prompt (JSON)
```

### Prompt Generation

Both modes use the same prompt generation process:

1. Tests Ollama connectivity
2. Requests Instagram-style prompt from LLM
3. Falls back to built-in template if Ollama unavailable
4. Uses the prompt for image generation

**Both local and online modes produce the same high-quality prompts!**

## Configuration

### Environment Variables

| Variable | Purpose | Example |
|----------|---------|----------|
| `SD_API_KEY` | ModelsLab API key | `export SD_API_KEY='abc123...'` |
| `SD_SERVICE` | Default service (`local`/`modelslab`) | `export SD_SERVICE='modelslab'` |

### Files

- `generated_prompts.json` — Saved prompts by topic (auto-generated)
- `config.json` — Optional: `{"api_key": "your_key"}`

## Local vs Online Comparison

| Feature | Local Mode | Online Mode |
|---------|-----------|-------------|
| **Installation** | Requires SDAPI | No installation |
| **Speed** | Depends on GPU (typically fast) | Network dependent (~10-30s) |
| **Cost** | Free (compute only) | Free (ModelsLab) |
| **Privacy** | 100% local | Prompts sent to API |
| **Offline** | ✓ Yes | ✗ No |
| **Rate Limits** | None | Yes (check provider) |
| **Best For** | Frequent use, powerful GPU | Quick testing, no GPU |

## Troubleshooting

### Ollama Connection Error (Both Modes)

```bash
Error connecting to Ollama: Connection refused
```

**Solution:**
```bash
ollama serve
curl http://127.0.0.1:11434/api/tags  # Verify
```

### Local Mode: SDAPI Connection Error

```bash
Request to SDAPI failed: Connection refused
```

**Solution:**
1. Ensure SDAPI is running on port 8141
2. Check your model directory is mounted/volumed correctly
3. Try: `python3 app.py topic --online` instead

### Online Mode: API Key Error

```bash
Error: API key required for online service
```

**Solution:**
1. Get free key from https://modelslab.com/
2. Set it: `export SD_API_KEY='your_key'`
3. Or use: `python3 app.py topic --online --api-key your_key`

### Online Mode: Rate Limited

```bash
Error: Rate limited. Please wait before trying again.
```

**Solution:**
- Wait a few minutes
- Switch to local mode if available
- Check provider's rate limits

### Missing Dependencies

```bash
pip install requests
```

## Switching Between Modes

### If Local Installation Fails

```bash
# Try online mode instead
python3 app.py "coffee" --online
```

### If You Want to Go Local

1. Setup SDAPI on port 8141
2. Run without `--online` flag

### Best Practice

```bash
# Set your preferred default in environment
export SD_SERVICE='modelslab'  # or 'local'

# Then just run normally
python3 app.py "coffee"
```

## Development

See [RULES_coding.md](RULES_coding.md) for coding standards.

### Testing Both Modes

```bash
# Quick test (1 step)
python3 app.py "test" -s 1 --online

# Local test
python3 app.py "test" -s 1 --service local
```

## API Reference

### ModelsLab Online API

- **Endpoint**: `POST https://modelslab.com/api/v6/images/text2img`
- **Auth**: API key (free from https://modelslab.com/)
- **Format**: JSON with prompt, steps, dimensions
- **Response**: Base64-encoded PNG (same format as local SD)

### Local SDAPI

- **Endpoint**: `GET http://127.0.0.1:8141/generate`
- **Auth**: None (local only)
- **Format**: Query parameters with prompt, steps
- **Response**: PNG binary (code converts to base64)

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for:
- System diagrams
- Component details
- Data flow
- Error handling

## Future Enhancements

See [ARCHITECTURE.md](ARCHITECTURE.md#future-enhancements) for planned features including:
- Additional online providers (HuggingFace, Replicate)
- Batch generation
- Custom negative prompts
- Model selection

## License

MIT License

## Support

For issues:
1. Check troubleshooting section above
2. Verify your service (local vs online)
3. Check that Ollama is running (for prompt generation)
4. For online mode, verify your API key
5. Review [ARCHITECTURE.md](ARCHITECTURE.md) for system details

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review `ARCHITECTURE.md` for system details
3. Review `PROMPT_Instructions.md` for prompt guidelines# imagepromptgenerator
