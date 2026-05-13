import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
OUTPUT_DIR = BASE_DIR / "output"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
for path in [ASSETS_DIR, OUTPUT_DIR, LOGS_DIR, OUTPUT_DIR / "audio", OUTPUT_DIR / "segments"]:
    path.mkdir(parents=True, exist_ok=True)

# API Keys
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")

# Streaming Settings
RTMP_URL = os.getenv("RTMP_URL")  # YouTube RTMP URL + Stream Key
STREAM_RESOLUTION = "1920x1080"
STREAM_FPS = 30
STREAM_BITRATE = "4500k"

# Generation Settings
MUSIC_PROMPT = "lofi hip hop, chill beats, relax, study, atmospheric"
SONG_DURATION = 120  # seconds
QUEUE_MIN_SIZE = 5

# Fallback Settings
FALLBACK_MUSIC_DIR = ASSETS_DIR / "music"
FALLBACK_VIDEO_DIR = ASSETS_DIR / "videos"

# Visual Settings
FONT_PATH = "C:/Windows/Fonts/arial.ttf"  # Update for Linux: "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
TEXT_COLOR = "white"
TEXT_SIZE = 48
