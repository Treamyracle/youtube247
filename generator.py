import torch

import random
import time
from pathlib import Path
from loguru import logger
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write
from config import OUTPUT_DIR, FALLBACK_MUSIC_DIR, MUSIC_PROMPT, SONG_DURATION

# Configure logger
logger.add("logs/generator.log", rotation="10 MB")

class MusicGenerator:
    def __init__(self, model_name='facebook/musicgen-small'):
        """
        Initializes the Local MusicGen model using DirectML for AMD GPUs.
        """
        try:
            logger.info(f"Initializing Local MusicGen ({model_name}) on AMD GPU...")
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model = MusicGen.get_pretrained(model_name)
            self.model.to(self.device)
            logger.info("Local MusicGen initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize local model: {e}")
            self.model = None

    def generate_song(self, prompt=None):
        """Generates a song locally using your GPU."""
        if not self.model:
            logger.warning("Local model not available. Using fallback.")
            return self.get_fallback_song()

        try:
            prompt = prompt or MUSIC_PROMPT
            logger.info(f"Generating song locally: '{prompt}' for {SONG_DURATION}s")

            # Set generation parameters
            self.model.set_generation_params(duration=SONG_DURATION)
            
            # Generate
            # We wrap in a list because the model expects a list of prompts
            wav = self.model.generate([prompt])
            
            # Save the file
            timestamp = int(time.time())
            file_base_path = OUTPUT_DIR / "audio" / f"song_{timestamp}"
            
            # audio_write adds the .wav extension automatically
            # wav[0] because we generated one prompt
            actual_path = audio_write(
                str(file_base_path), 
                wav[0].cpu(), 
                self.model.sample_rate, 
                strategy="loudness", 
                loudness_compressor=True
            )
            
            logger.info(f"Local song generated and saved to: {actual_path}")
            return Path(actual_path)
            
        except Exception as e:
            logger.error(f"Error during local generation: {e}")
            return self.get_fallback_song()

    def get_fallback_song(self):
        """Returns a random song from the fallback directory."""
        logger.info("Fetching fallback song...")
        fallback_files = list(FALLBACK_MUSIC_DIR.glob("*.mp3")) + list(FALLBACK_MUSIC_DIR.glob("*.wav"))
        if not fallback_files:
            logger.error("No fallback music found in assets/music!")
            return None
        
        selected = random.choice(fallback_files)
        logger.info(f"Selected fallback song: {selected}")
        return selected

if __name__ == "__main__":
    # Test local generation
    gen = MusicGenerator(model_name='facebook/musicgen-small') # Small is faster for testing
    gen.generate_song()
