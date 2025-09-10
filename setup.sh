#!/bin/bash

echo "Setting up Chatterbox TTS WebSocket API environment..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Please install uv first:"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "Creating virtual environment with uv..."
uv venv

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing dependencies..."
uv pip install -e .

echo "Downloading models (this may take a while)..."
python -c "
from chatterbox.tts import ChatterboxTTS
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
import torch

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f'Downloading models for device: {device}')

try:
    ChatterboxTTS.from_pretrained(device)
    ChatterboxMultilingualTTS.from_pretrained(device)
    print('Models downloaded successfully!')
except Exception as e:
    print(f'Error downloading models: {e}')
    print('You can download them later when starting the server.')
"

echo ""
echo "Setup complete! You can now:"
echo "1. Start the server: ./start.sh"
echo "2. Test the service: ./test.sh"
echo ""
