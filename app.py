#!/usr/bin/env python3
"""Instagram Photo Generator CLI application.

Generates Instagram-worthy photos based on user-provided topics by combining
LLM-powered prompt generation (via Ollama) with AI image synthesis (via Stable
Diffusion).

External Dependencies:
    - Ollama running on localhost:11434 (for prompt generation)
    - Stable Diffusion Web UI on localhost:7860 (for local image generation), OR
    - ModelsLab API key (for online image generation without local installation)

Usage:
    python3 app.py "coffee" [-o output_folder] [-s diffusion_steps]
    python3 app.py "coffee" --online [--api-key KEY]
"""

import argparse
import base64
import json
import os
import sys
from typing import Dict, List, Optional, Protocol

import requests

# ============================
# Configuration Constants
# ============================
PROMPTS_FILE: str = "generated_prompts.json"
OLLAMA_URL: str = "http://127.0.0.1:11434"
SD_WEBUI_URL: str = "http://127.0.0.1:7860"
OLLAMA_MODEL: str = "llama2-uncensored:7b"
OLLAMA_TEST_TIMEOUT: int = 10
OLLAMA_GENERATE_TIMEOUT: int = 120
SD_API_TIMEOUT: int = 120

# Online service configuration
MODELSLAB_API_URL: str = "https://modelslab.com/api/v6/images/text2img"
DEFAULT_SERVICE: str = "local"
DEFAULT_MODEL_ID: str = "stable-diffusion-xl-1024-v1-0"

# Environment variable names
ENV_SD_API_KEY: str = "SD_API_KEY"
ENV_SD_SERVICE: str = "SD_SERVICE"


# ============================
# Prompt Persistence
# ============================
def load_prompts() -> Dict[str, List[str]]:
    """Load existing prompts from JSON file, handling legacy format migration.
    
    Reads the prompts file and automatically migrates old format
    (with 'prompts' list key) to new topic-based format.
    
    Returns:
        Dictionary mapping topic names to lists of prompts.
        Returns empty dict if file doesn't exist or on error.
    """
    if not os.path.exists(PROMPTS_FILE):
        return {}
    
    try:
        with open(PROMPTS_FILE, 'r') as f:
            data: Dict = json.load(f)
        
        # Check if it's the old format ({"prompts": [...]})
        if "prompts" in data and isinstance(data["prompts"], list):
            # Migrate old format to new topic-based format
            migrated: Dict[str, List[str]] = {"general": data["prompts"]}
            print(
                f"Migrated {len(data['prompts'])} prompts "
                f"from legacy format to 'general' topic"
            )
            return migrated
        
        return data
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading prompts file '{PROMPTS_FILE}': {e}")
        return {}


def save_prompts(prompts: Dict[str, List[str]]) -> bool:
    """Save prompts to JSON file.
    
    Args:
        prompts: Dictionary mapping topic names to lists of prompts.
    
    Returns:
        True on success, False on error.
    """
    try:
        with open(PROMPTS_FILE, 'w') as f:
            json.dump(prompts, f, indent=2)
        return True
    except IOError as e:
        print(f"Error saving prompts file '{PROMPTS_FILE}': {e}")
        return False


def add_prompt_to_topic(
    topic: str,
    prompt: str,
    prompts: Dict[str, List[str]]
) -> Dict[str, List[str]]:
    """Add a prompt to a topic, extending existing prompts if present.
    
    Normalizes topic to lowercase for consistency. Creates new topic
    entry if it doesn't exist.
    
    Args:
        topic: The topic name/category.
        prompt: The Instagram prompt to add.
        prompts: Current prompts dictionary.
    
    Returns:
        Updated prompts dictionary.
    """
    topic_key: str = topic.lower().strip()
    
    if topic_key in prompts:
        prompts[topic_key].append(prompt)
        print(
            f"Extended existing topic '{topic_key}' "
            f"(now has {len(prompts[topic_key])} prompts)"
        )
    else:
        prompts[topic_key] = [prompt]
        print(f"Created new topic '{topic_key}'")
    
    return prompts


# ============================
# Image Generation Service
# ============================

class ImageGenerationService(Protocol):
    """Protocol for image generation services.
    
    Any service that implements generate() can be used for image synthesis.
    """
    
    def generate(self, prompt: str, steps: int) -> Optional[str]:
        ...


class LocalStableDiffusionService:
    """Image generation using local Stable Diffusion Web UI.
    
    Connects to a local Stable Diffusion Web UI instance via its REST API.
    Requires SD Web UI running on the specified URL.
    """
    
    def __init__(self, url: str = SD_WEBUI_URL) -> None:
        """Initialize local SD service.
        
        Args:
            url: Base URL of the Stable Diffusion Web UI API.
        """
        self.url: str = url
    
    def generate(self, prompt: str, steps: int) -> Optional[str]:
        """Generate image from prompt using local Stable Diffusion.
        
        Args:
            prompt: The image generation prompt.
            steps: Number of diffusion steps (1-100).
        
        Returns:
            Base64-encoded PNG image data, or None on failure.
        """
        payload: Dict[str, str | int] = {
            "prompt": prompt,
            "steps": steps,
        }
        
        try:
            response = requests.post(
                f"{self.url}/sdapi/v1/txt2img",
                json=payload,
                timeout=SD_API_TIMEOUT,
            )
            response.raise_for_status()
            
            data: Dict = response.json()
            images: List[str] = data.get("images", [])
            
            if not images:
                print("No images returned from Stable Diffusion API")
                return None
            
            return images[0]
            
        except requests.exceptions.RequestException as e:
            print(f"Request to Stable Diffusion API failed: {e}")
        except (KeyError, IndexError) as e:
            print(f"Unexpected response format from API: {e}")
        except json.JSONDecodeError as e:
            print(f"Invalid JSON response: {e}")
        
        return None


class ModelsLabOnlineService:
    """Image generation using ModelsLab online Stable Diffusion API.
    
    Free online service that generates images without requiring local
    Stable Diffusion installation. Requires a free API key from
    https://modelslab.com/.
    """
    
    def __init__(self, api_key: str, model_id: str = DEFAULT_MODEL_ID) -> None:
        """Initialize ModelsLab online service.
        
        Args:
            api_key: Free API key from ModelsLab.
            model_id: Model to use (default: SDXL).
        """
        self.api_key: str = api_key
        self.model_id: str = model_id
    
    def generate(self, prompt: str, steps: int) -> Optional[str]:
        """Generate image from prompt using ModelsLab API.
        
        Args:
            prompt: The image generation prompt.
            steps: Number of diffusion steps (1-50). Maps to num_inference_steps.
        
        Returns:
            Base64-encoded PNG image data, or None on failure.
        """
        # Clamp steps for online API (typically 1-50)
        clamped_steps: int = max(1, min(steps, 50))
        
        payload: Dict[str, str | int] = {
            "key": self.api_key,
            "model_id": self.model_id,
            "prompt": prompt,
            "negative_prompt": (
                "disfigured, deformed, ugly, bad anatomy, blurry, low quality, "
                "cartoon, anime, 3d, painting, watermark, text"
            ),
            "width": "768",
            "height": "768",
            "samples": "1",
            "num_inference_steps": str(clamped_steps),
            "safety_checker": "no",
            "enhance_prompt": "yes",
        }
        
        try:
            response = requests.post(
                MODELSLAB_API_URL,
                json=payload,
                timeout=SD_API_TIMEOUT,
            )
            
            if response.status_code == 401:
                print("Error: Invalid API key. Please check your ModelsLab API key.")
                return None
            elif response.status_code == 429:
                print("Error: Rate limited. Please wait before trying again.")
                return None
            elif response.status_code != 200:
                print(f"API returned status {response.status_code}")
                return None
            
            data: Dict = response.json()
            
            if data.get("status") != "success":
                print(f"API error: {data.get('message', 'Unknown error')}")
                return None
            
            images: List[str] = data.get("images", [])
            
            if not images:
                print("No images returned from API")
                return None
            
            print("(Generated via ModelsLab online service)")
            return images[0]
            
        except requests.exceptions.Timeout:
            print("Request timed out. Please try again.")
        except requests.exceptions.ConnectionError:
            print("Could not connect to online service. Check your internet connection.")
        except requests.exceptions.RequestException as e:
            print(f"Request to ModelsLab API failed: {e}")
        except (KeyError, IndexError) as e:
            print(f"Unexpected response format: {e}")
        except json.JSONDecodeError as e:
            print(f"Invalid JSON response: {e}")
        
        return None


def get_api_key(cli_api_key: Optional[str]) -> Optional[str]:
    """Get API key from CLI argument, environment, or config file.
    
    Priority order:
    1. CLI argument (--api-key)
    2. Environment variable (SD_API_KEY)
    3. Config file (config.json)
    
    Args:
        cli_api_key: API key from CLI, if provided.
    
    Returns:
        API key string, or None if not found.
    """
    if cli_api_key:
        return cli_api_key
    
    env_key = os.environ.get(ENV_SD_API_KEY)
    if env_key:
        return env_key
    
    # Try config.json
    try:
        if os.path.exists("config.json"):
            with open("config.json", 'r') as f:
                config: Dict = json.load(f)
                return config.get("api_key")
    except (IOError, json.JSONDecodeError):
        pass
    
    return None


# ============================
# Prompt Generation
# ============================
def test_ollama_connection() -> bool:
    """Test basic connectivity to Ollama service.
    
    Returns:
        True if Ollama responds successfully, False otherwise.
    """
    test_url: str = f"{OLLAMA_URL}/api/generate"
    payload: Dict[str, str | bool] = {
        "model": OLLAMA_MODEL,
        "prompt": "Say hello",
        "stream": False,
    }
    
    try:
        response = requests.post(
            test_url,
            json=payload,
            timeout=OLLAMA_TEST_TIMEOUT,
        )
        status_ok: bool = response.status_code == 200
        if status_ok:
            result: str = response.json().get('response', '').strip()
            print(f"Ollama test response: {result}")
        else:
            print(f"Ollama test returned status {response.status_code}")
        return status_ok
    except requests.exceptions.RequestException as e:
        print(f"Ollama connection test failed: {e}")
        return False


def generate_instagram_prompt_from_ollama(topic: str) -> Optional[str]:
    """Request an Instagram-style prompt from Ollama for the given topic.
    
    Args:
        topic: The photo topic/subject.
    
    Returns:
        Generated prompt string, or None if the request fails.
    """
    generate_url: str = f"{OLLAMA_URL}/api/generate"
    prompt: str = (
        f"You are a professional photographer. Generate ONE creative "
        f"Instagram-worthy photo prompt for the topic: '{topic}'. "
        "The prompt should be a vivid, detailed description of the scene.\n\n"
        "Rules:\n"
        "1. Replace the topic with an actual description\n"
        "2. Add specific details: setting, lighting, colors, mood\n"
        "3. Include camera terms: smartphone, iPhone, shallow depth of field\n"
        "4. Add quality terms: 8K UHD, highly detailed, sharp focus\n"
        "5. Make it Instagram-worthy and visually appealing\n\n"
        "Example output for topic 'coffee':\n"
        "artisan latte with heart foam art on rustic wooden table, "
        "cozy coffee shop with warm golden hour light streaming through "
        "window, exposed brick wall background, smartphone photography, "
        "iPhone 15 Pro Max, shallow depth of field, warm color tones, "
        "lifestyle photography, Instagram-worthy, highly detailed foam art, "
        "steam rising, morning vibes, 8K UHD\n\n"
        f"Now generate a prompt for topic '{topic}':\n"
    )
    
    payload: Dict[str, str | bool | int] = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
    }
    
    try:
        response = requests.post(
            generate_url,
            json=payload,
            timeout=OLLAMA_GENERATE_TIMEOUT,
        )
        
        if response.status_code == 200:
            result: str = response.json().get('response', '').strip()
            print(f"Generated prompt ({len(result)} characters)")
            return result
        
        print(f"Ollama returned status {response.status_code}")
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"Ollama request failed: {e}")
        return None


def _generate_fallback_instagram_prompt(topic: str) -> str:
    """Generate a fallback Instagram-style prompt.
    
    Used when Ollama is unavailable or fails. Provides a basic
    Instagram-style prompt structure for the given topic.
    
    Args:
        topic: The photo topic/subject.
    
    Returns:
        A formatted Instagram-style prompt string.
    """
    return (
        f"{topic}, aesthetic lifestyle photography, warm golden hour lighting, "
        "cozy setting with natural elements, smartphone photography, "
        "iPhone 15 Pro Max, shallow depth of field, warm color tones, "
        "lifestyle content, Instagram-worthy, aesthetic composition, "
        "highly detailed, 8K UHD, natural colors, professional quality, "
        "candid moment, trending, visually appealing, clean aesthetic"
    )


def get_instagram_prompt(topic: str) -> str:
    """Generate an Instagram-style photo prompt for the given topic.
    
    Attempts to use Ollama LLM for creative prompt generation.
    Falls back to a built-in template if Ollama is unavailable.
    
    Args:
        topic: The photo topic/subject (e.g., "coffee", "travel").
    
    Returns:
        A detailed Instagram-style prompt string.
    """
    print("Testing Ollama connection...")
    
    if test_ollama_connection():
        print(f"Generating Instagram prompt for topic: {topic}...")
        prompt = generate_instagram_prompt_from_ollama(topic)
        if prompt:
            return prompt
    
    print("Using fallback Instagram prompt")
    return _generate_fallback_instagram_prompt(topic)


# ============================
# Image Generation
# ============================


def create_service(
    service_type: str,
    api_key: Optional[str] = None,
    url: str = SD_WEBUI_URL,
) -> ImageGenerationService:
    """Factory function to create an image generation service.
    
    Args:
        service_type: Type of service ("local" or "modelslab").
        api_key: API key for online services (required for modelslab).
        url: URL for local Stable Diffusion Web UI.
    
    Returns:
        An ImageGenerationService instance.
    
    Raises:
        ValueError: If service_type is unknown or api_key is missing.
    """
    if service_type == "local":
        return LocalStableDiffusionService(url)
    elif service_type == "modelslab":
        if not api_key:
            raise ValueError(
                "API key required for modelslab service. "
                "Get a free key from https://modelslab.com/ "
                "or set SD_API_KEY environment variable."
            )
        return ModelsLabOnlineService(api_key)
    else:
        raise ValueError(
            f"Unknown service type: {service_type}. "
            f"Choose from: local, modelslab"
        )


def generate_image(
    prompt: str,
    service: ImageGenerationService,
    steps: int = 20,
) -> Optional[str]:
    """Generate an image from a prompt using the given service.
    
    Args:
        prompt: The image generation prompt.
        service: Image generation service instance.
        steps: Number of diffusion steps.
    
    Returns:
        Base64-encoded PNG image data, or None on failure.
    """
    return service.generate(prompt, steps)


# ============================
# Output Management
# ============================
def save_image(image_data: str, filename: str, folder: str) -> None:
    """Save base64-encoded image data to a PNG file.
    
    Creates the output directory if it doesn't exist.
    
    Args:
        image_data: Base64-encoded image data.
        filename: Output filename (e.g., "instagram_coffee.png").
        folder: Output directory path.
    
    Raises:
        OSError: If file operations fail.
        ValueError: If image_data is empty.
    """
    if not image_data:
        raise ValueError("Image data cannot be empty")
    
    os.makedirs(folder, exist_ok=True)
    filepath: str = os.path.join(folder, filename)
    with open(filepath, 'wb') as f:
        f.write(base64.b64decode(image_data))


# ============================
# Main Application
# ============================
def parse_arguments() -> argparse.Namespace:
    """Parse and validate command-line arguments.
    
    Returns:
        Parsed arguments namespace.
    
    Raises:
        SystemExit: If arguments are invalid.
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description='Generate Instagram-style photos based on a topic',
    )
    parser.add_argument(
        'topic',
        type=str,
        help='The topic for the Instagram-style photo '
             '(e.g., "coffee", "travel", "fitness")',
    )
    parser.add_argument(
        '-o',
        '--output',
        type=str,
        default='generated_images',
        help='Output folder for generated images (default: generated_images)',
    )
    parser.add_argument(
        '-s',
        '--steps',
        type=int,
        default=20,
        help='Number of diffusion steps (default: 20)',
    )
    parser.add_argument(
        '--online',
        action='store_true',
        help='Use online Stable Diffusion service (requires API key).',
    )
    parser.add_argument(
        '--api-key',
        type=str,
        default=None,
        help='API key for online service (or set SD_API_KEY env var).',
    )
    parser.add_argument(
        '--service',
        type=str,
        choices=['local', 'modelslab'],
        default=os.environ.get(ENV_SD_SERVICE, DEFAULT_SERVICE),
        help='Image generation service (default: local).',
    )
    
    return parser.parse_args()


def main() -> None:
    """Main application entry point.
    
    Orchestrates the complete workflow: argument parsing, prompt generation,
    image synthesis, and output persistence.
    """
    args: argparse.Namespace = parse_arguments()
    topic: str = args.topic.strip()
    
    if not topic:
        print("Error: Topic cannot be empty")
        sys.exit(1)
    
    # Determine service type and API key
    service_type: str = args.service
    api_key: Optional[str] = args.api_key
    
    if args.online:
        service_type = "modelslab"
    
    if service_type == "modelslab" and not api_key:
        api_key = get_api_key(None)
        if not api_key:
            print(
                "Error: API key required for online service.\n"
                "Get a free key from https://modelslab.com/\n"
                "Then set it with:\n"
                "  export SD_API_KEY='your_key'\n"
                "  # or\n"
                "  python3 app.py 'topic' --api-key your_key\n"
            )
            sys.exit(1)
    
    print(f"{'=' * 60}")
    print(f"Instagram Photo Generator")
    print(f"Topic: {topic}")
    print(f"Output folder: {args.output}")
    print(f"Steps: {args.steps}")
    print(f"Service: {service_type}")
    print(f"{'=' * 60}")
    
    # Create image generation service
    try:
        service = create_service(service_type, api_key)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Load existing prompts (handles legacy format migration)
    prompts: Dict[str, List[str]] = load_prompts()
    print(f"Loaded {len(prompts)} topic(s) from {PROMPTS_FILE}")
    
    # Generate Instagram-style prompt based on topic
    prompt: str = get_instagram_prompt(topic)
    print(f"\nGenerated Prompt:\n{prompt}\n")
    
    # Add prompt to topic and persist
    prompts = add_prompt_to_topic(topic, prompt, prompts)
    if save_prompts(prompts):
        print(f"Prompts saved to {PROMPTS_FILE}")
    
    # Generate the image
    print("Generating image...")
    img_data: Optional[str] = generate_image(prompt, service, steps=args.steps)
    
    if img_data:
        # Create safe filename from topic
        safe_topic: str = ''.join(
            c if c.isalnum() else '_' for c in topic
        )
        output_filename: str = f"instagram_{safe_topic}.png"
        
        try:
            save_image(img_data, output_filename, args.output)
            print(f"\nImage generated successfully!")
            print(f"Saved to: {args.output}/{output_filename}")
        except (OSError, ValueError) as e:
            print(f"\nFailed to save image: {e}")
            sys.exit(1)
    else:
        if service_type == "modelslab":
            print(
                "\nFailed to generate image via online service.\n"
                "To use local Stable Diffusion instead, run without --online"
            )
        else:
            print(
                "\nFailed to generate image via local service.\n"
                "To use online service instead, run with --online"
            )
        sys.exit(1)


if __name__ == "__main__":
    main()
