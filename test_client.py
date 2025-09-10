import asyncio
import json
import base64
import argparse
import logging
from websockets.client import connect
from websockets.exceptions import ConnectionClosed

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatterboxTestClient:
    def __init__(self, uri: str = "ws://localhost:8000"):
        self.uri = uri
    
    def _encode_audio_file(self, file_path: str) -> str:
        """Encode audio file to base64 string."""
        try:
            with open(file_path, 'rb') as f:
                audio_data = f.read()
            return base64.b64encode(audio_data).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to encode audio file: {e}")
            raise
    
    def _save_audio(self, base64_audio: str, output_path: str):
        """Save base64 audio to file."""
        try:
            audio_data = base64.b64decode(base64_audio)
            with open(output_path, 'wb') as f:
                f.write(audio_data)
            logger.info(f"Audio saved to: {output_path}")
        except Exception as e:
            logger.error(f"Failed to save audio: {e}")
            raise
    
    async def test_basic_tts(self, text: str, language: str = "es", output_file: str = "test_output.wav"):
        """Test basic TTS functionality."""
        logger.info(f"Testing TTS with text: '{text}' in language: {language}")
        
        try:
            async with connect(self.uri) as websocket:
                # Send TTS request
                request = {
                    "type": "tts_request",
                    "data": {
                        "text": text,
                        "config": {
                            "language_id": language,
                            "exaggeration": 0.5,
                            "temperature": 0.8,
                            "cfg_weight": 0.5
                        }
                    }
                }
                
                await websocket.send(json.dumps(request))
                logger.info("TTS request sent")
                
                # Wait for responses (server sends server_info first, then tts_response)
                tts_response_received = False
                while not tts_response_received:
                    response = await websocket.recv()
                    response_data = json.loads(response)
                    
                    if response_data.get("type") == "tts_response":
                        tts_response_received = True
                    elif response_data.get("type") == "server_info":
                        logger.info("Received server info, waiting for TTS response...")
                        continue
                    else:
                        logger.warning(f"Unexpected response type: {response_data.get('type')}")
                        continue
                
                if response_data.get("type") == "tts_response":
                    data = response_data.get("data", {})
                    if data.get("status") == "success":
                        logger.info("TTS generation successful!")
                        logger.info(f"Sample rate: {data.get('sample_rate')}")
                        logger.info(f"Language: {data.get('language')}")
                        
                        # Save audio
                        if data.get("audio"):
                            self._save_audio(data["audio"], output_file)
                        else:
                            logger.error("No audio data received")
                    else:
                        logger.error(f"TTS generation failed: {data.get('message')}")
                else:
                    logger.error(f"Unexpected response type: {response_data.get('type')}")
                
        except ConnectionClosed:
            logger.error("Connection closed unexpectedly")
        except Exception as e:
            logger.error(f"Error in test: {e}")
    
    async def test_with_reference_audio(self, text: str, reference_audio_path: str, 
                                      language: str = "es", output_file: str = "test_with_ref.wav"):
        """Test TTS with reference audio."""
        logger.info(f"Testing TTS with reference audio: {reference_audio_path}")
        
        try:
            # Encode reference audio
            reference_audio_b64 = self._encode_audio_file(reference_audio_path)
            
            async with connect(self.uri) as websocket:
                # Send TTS request with reference audio
                request = {
                    "type": "tts_request",
                    "data": {
                        "text": text,
                        "reference_audio": reference_audio_b64,
                        "config": {
                            "language_id": language,
                            "exaggeration": 0.7,
                            "temperature": 0.8,
                            "cfg_weight": 0.5
                        }
                    }
                }
                
                await websocket.send(json.dumps(request))
                logger.info("TTS request with reference audio sent")
                
                # Wait for responses (server sends server_info first, then tts_response)
                tts_response_received = False
                while not tts_response_received:
                    response = await websocket.recv()
                    response_data = json.loads(response)
                    
                    if response_data.get("type") == "tts_response":
                        tts_response_received = True
                    elif response_data.get("type") == "server_info":
                        logger.info("Received server info, waiting for TTS response...")
                        continue
                    else:
                        logger.warning(f"Unexpected response type: {response_data.get('type')}")
                        continue
                
                if response_data.get("type") == "tts_response":
                    data = response_data.get("data", {})
                    if data.get("status") == "success":
                        logger.info("TTS generation with reference audio successful!")
                        logger.info(f"Sample rate: {data.get('sample_rate')}")
                        logger.info(f"Language: {data.get('language')}")
                        
                        # Save audio
                        if data.get("audio"):
                            self._save_audio(data["audio"], output_file)
                        else:
                            logger.error("No audio data received")
                    else:
                        logger.error(f"TTS generation failed: {data.get('message')}")
                else:
                    logger.error(f"Unexpected response type: {response_data.get('type')}")
                
        except ConnectionClosed:
            logger.error("Connection closed unexpectedly")
        except Exception as e:
            logger.error(f"Error in test: {e}")
    
    async def test_ping(self):
        """Test server ping."""
        logger.info("Testing server ping")
        
        try:
            async with connect(self.uri) as websocket:
                # Send ping
                ping_request = {
                    "type": "ping",
                    "data": {}
                }
                
                await websocket.send(json.dumps(ping_request))
                logger.info("Ping sent")
                
                # Wait for pong
                response = await websocket.recv()
                response_data = json.loads(response)
                
                if response_data.get("type") == "pong":
                    logger.info("Pong received - server is alive!")
                else:
                    logger.error(f"Unexpected response to ping: {response_data.get('type')}")
                
        except ConnectionClosed:
            logger.error("Connection closed unexpectedly")
        except Exception as e:
            logger.error(f"Error in ping test: {e}")
    
    async def test_server_info(self):
        """Test server info retrieval."""
        logger.info("Testing server info")
        
        try:
            async with connect(self.uri) as websocket:
                # Wait for welcome message
                response = await websocket.recv()
                response_data = json.loads(response)
                
                if response_data.get("type") == "server_info":
                    data = response_data.get("data", {})
                    logger.info("Server info received:")
                    logger.info(f"  Message: {data.get('message')}")
                    logger.info(f"  Supported languages: {data.get('supported_languages')}")
                    logger.info(f"  Default language: {data.get('default_language')}")
                    logger.info(f"  Device: {data.get('device')}")
                else:
                    logger.error(f"Unexpected welcome message: {response_data.get('type')}")
                
        except ConnectionClosed:
            logger.error("Connection closed unexpectedly")
        except Exception as e:
            logger.error(f"Error in server info test: {e}")

async def main():
    """Main function to run tests."""
    parser = argparse.ArgumentParser(description="Chatterbox TTS WebSocket Test Client")
    parser.add_argument("--uri", default="ws://localhost:8000", help="WebSocket server URI")
    parser.add_argument("--text", default="Hola, este es un test del sistema de síntesis de voz Chatterbox.", 
                       help="Text to synthesize")
    parser.add_argument("--language", default="es", help="Language code (default: es)")
    parser.add_argument("--reference-audio", help="Path to reference audio file")
    parser.add_argument("--output", default="test_output.wav", help="Output audio file")
    parser.add_argument("--test", choices=["basic", "reference", "ping", "info", "all"], 
                       default="all", help="Test to run")
    
    args = parser.parse_args()
    
    client = ChatterboxTestClient(args.uri)
    
    logger.info(f"Starting tests against server: {args.uri}")
    
    try:
        if args.test == "basic" or args.test == "all":
            await client.test_basic_tts(args.text, args.language, args.output)
        
        if args.test == "reference" or args.test == "all":
            if args.reference_audio:
                await client.test_with_reference_audio(
                    args.text, args.reference_audio, args.language, 
                    f"ref_{args.output}"
                )
            else:
                logger.warning("No reference audio provided, skipping reference test")
        
        if args.test == "ping" or args.test == "all":
            await client.test_ping()
        
        if args.test == "info" or args.test == "all":
            await client.test_server_info()
        
        logger.info("All tests completed!")
        
    except KeyboardInterrupt:
        logger.info("Tests interrupted by user")
    except Exception as e:
        logger.error(f"Test error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
