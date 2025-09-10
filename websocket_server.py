import asyncio
import json
import base64
import io
import tempfile
import os
import logging
from typing import Optional, Dict, Any
import torch
import torchaudio
import numpy as np
from websockets.server import serve
from websockets.exceptions import ConnectionClosed
import traceback

from chatterbox.mtl_tts import ChatterboxMultilingualTTS, SUPPORTED_LANGUAGES

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatterboxWebSocketServer:
    def __init__(self, host: str = "localhost", port: int = 8000):
        self.host = host
        self.port = port
        self.model = None
        self.device = self._get_device()
        
    def _get_device(self) -> str:
        """Automatically detect the best available device."""
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"
    
    async def load_model(self):
        """Load the multilingual TTS model."""
        if self.model is None:
            logger.info(f"Loading Chatterbox Multilingual TTS model on device: {self.device}")
            try:
                self.model = ChatterboxMultilingualTTS.from_pretrained(self.device)
                logger.info("Model loaded successfully!")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                raise
    
    def _decode_audio(self, base64_audio: str) -> str:
        """Decode base64 audio and save to temporary file."""
        try:
            audio_data = base64.b64decode(base64_audio)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file.write(audio_data)
                return temp_file.name
        except Exception as e:
            logger.error(f"Failed to decode audio: {e}")
            raise ValueError("Invalid base64 audio data")
    
    def _encode_audio(self, audio_tensor: torch.Tensor, sample_rate: int) -> str:
        """Encode audio tensor to base64 string."""
        temp_file_path = None
        try:
            # Convert tensor to numpy array
            if isinstance(audio_tensor, torch.Tensor):
                audio_np = audio_tensor.squeeze().cpu().numpy()
            else:
                audio_np = audio_tensor
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file_path = temp_file.name
                torchaudio.save(temp_file_path, torch.from_numpy(audio_np).unsqueeze(0), sample_rate)
            
            # Read the file and encode to base64
            with open(temp_file_path, 'rb') as f:
                audio_data = f.read()
            
            return base64.b64encode(audio_data).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Failed to encode audio: {e}")
            raise
        finally:
            # Clean up temporary file with error handling
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except (PermissionError, OSError) as e:
                    logger.warning(f"Could not delete temporary file {temp_file_path}: {e}")
                    # On Windows, sometimes files are still locked, so we'll just leave them
                    # The temp directory will be cleaned up by the OS eventually
    
    def _validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and set default values for configuration."""
        defaults = {
            "language_id": "es",  # Default to Spanish
            "exaggeration": 0.5,
            "temperature": 0.8,
            "cfg_weight": 0.5,
            "repetition_penalty": 2.0,
            "min_p": 0.05,
            "top_p": 1.0
        }
        
        # Validate language_id
        if "language_id" in config:
            lang = config["language_id"].lower()
            if lang not in SUPPORTED_LANGUAGES:
                raise ValueError(f"Unsupported language: {lang}. Supported languages: {list(SUPPORTED_LANGUAGES.keys())}")
            defaults["language_id"] = lang
        
        # Validate other parameters
        for key, default_value in defaults.items():
            if key in config:
                if key == "exaggeration" and not (0.25 <= config[key] <= 2.0):
                    raise ValueError("Exaggeration must be between 0.25 and 2.0")
                elif key == "temperature" and not (0.05 <= config[key] <= 5.0):
                    raise ValueError("Temperature must be between 0.05 and 5.0")
                elif key == "cfg_weight" and not (0.0 <= config[key] <= 1.0):
                    raise ValueError("CFG weight must be between 0.0 and 1.0")
                elif key == "repetition_penalty" and not (1.0 <= config[key] <= 3.0):
                    raise ValueError("Repetition penalty must be between 1.0 and 3.0")
                elif key == "min_p" and not (0.0 <= config[key] <= 1.0):
                    raise ValueError("Min_p must be between 0.0 and 1.0")
                elif key == "top_p" and not (0.0 <= config[key] <= 1.0):
                    raise ValueError("Top_p must be between 0.0 and 1.0")
                defaults[key] = config[key]
        
        return defaults
    
    async def process_tts_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a TTS request and return the response."""
        try:
            # Validate required fields
            if "text" not in data:
                raise ValueError("Missing required field: text")
            
            text = data["text"]
            if not text or not text.strip():
                raise ValueError("Text cannot be empty")
            
            # Limit text length
            if len(text) > 500:
                text = text[:500]
                logger.warning(f"Text truncated to 500 characters")
            
            # Get configuration
            config = data.get("config", {})
            config = self._validate_config(config)
            
            # Handle reference audio
            reference_audio_path = None
            if "reference_audio" in data and data["reference_audio"]:
                reference_audio_path = self._decode_audio(data["reference_audio"])
            
            logger.info(f"Generating TTS for text: '{text[:50]}...' in language: {config['language_id']}")
            
            # Generate audio
            with torch.inference_mode():
                audio_tensor = self.model.generate(
                    text=text,
                    language_id=config["language_id"],
                    audio_prompt_path=reference_audio_path,
                    exaggeration=config["exaggeration"],
                    temperature=config["temperature"],
                    cfg_weight=config["cfg_weight"],
                    repetition_penalty=config["repetition_penalty"],
                    min_p=config["min_p"],
                    top_p=config["top_p"]
                )
            
            # Encode audio to base64
            audio_base64 = self._encode_audio(audio_tensor, self.model.sr)
            
            # Clean up temporary reference audio file
            if reference_audio_path and os.path.exists(reference_audio_path):
                os.unlink(reference_audio_path)
            
            return {
                "type": "tts_response",
                "data": {
                    "audio": audio_base64,
                    "status": "success",
                    "message": f"Generated audio for '{config['language_id']}' text",
                    "sample_rate": self.model.sr,
                    "language": config["language_id"]
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing TTS request: {e}")
            logger.error(traceback.format_exc())
            
            # Clean up temporary reference audio file if it exists
            if "reference_audio_path" in locals() and reference_audio_path and os.path.exists(reference_audio_path):
                os.unlink(reference_audio_path)
            
            return {
                "type": "tts_response",
                "data": {
                    "audio": None,
                    "status": "error",
                    "message": str(e)
                }
            }
    
    async def handle_client(self, websocket, path):
        """Handle WebSocket client connections."""
        client_addr = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"Client connected: {client_addr}")
        
        try:
            # Send welcome message
            welcome_msg = {
                "type": "server_info",
                "data": {
                    "message": "Chatterbox TTS WebSocket Server",
                    "supported_languages": list(SUPPORTED_LANGUAGES.keys()),
                    "default_language": "es",
                    "device": self.device
                }
            }
            await websocket.send(json.dumps(welcome_msg))
            
            async for message in websocket:
                try:
                    # Parse incoming message
                    data = json.loads(message)
                    
                    if data.get("type") == "tts_request":
                        # Process TTS request
                        response = await self.process_tts_request(data.get("data", {}))
                        await websocket.send(json.dumps(response))
                    
                    elif data.get("type") == "ping":
                        # Handle ping
                        pong_response = {
                            "type": "pong",
                            "data": {"message": "Server is alive"}
                        }
                        await websocket.send(json.dumps(pong_response))
                    
                    else:
                        # Unknown message type
                        error_response = {
                            "type": "error",
                            "data": {
                                "message": f"Unknown message type: {data.get('type', 'unknown')}"
                            }
                        }
                        await websocket.send(json.dumps(error_response))
                
                except json.JSONDecodeError:
                    error_response = {
                        "type": "error",
                        "data": {
                            "message": "Invalid JSON format"
                        }
                    }
                    await websocket.send(json.dumps(error_response))
                
                except Exception as e:
                    logger.error(f"Error handling message: {e}")
                    error_response = {
                        "type": "error",
                        "data": {
                            "message": f"Internal server error: {str(e)}"
                        }
                    }
                    await websocket.send(json.dumps(error_response))
        
        except ConnectionClosed:
            logger.info(f"Client disconnected: {client_addr}")
        except Exception as e:
            logger.error(f"Error in client handler: {e}")
            logger.error(traceback.format_exc())
    
    async def start_server(self):
        """Start the WebSocket server."""
        await self.load_model()
        
        logger.info(f"Starting Chatterbox TTS WebSocket server on {self.host}:{self.port}")
        logger.info(f"Device: {self.device}")
        logger.info(f"Supported languages: {list(SUPPORTED_LANGUAGES.keys())}")
        
        async with serve(self.handle_client, self.host, self.port):
            logger.info("Server is running. Press Ctrl+C to stop.")
            await asyncio.Future()  # Run forever

def main():
    """Main function to start the server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Chatterbox TTS WebSocket Server")
    parser.add_argument("--host", default="localhost", help="Host to bind to (default: localhost)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to (default: 8000)")
    
    args = parser.parse_args()
    
    server = ChatterboxWebSocketServer(args.host, args.port)
    
    try:
        asyncio.run(server.start_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()
