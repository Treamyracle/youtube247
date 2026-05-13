import subprocess
import time
import os
from pathlib import Path
from loguru import logger
from config import RTMP_URL, OUTPUT_DIR

class Streamer:
    def __init__(self):
        self.playlist_path = OUTPUT_DIR / "playlist.txt"
        self.process = None

    def update_playlist(self, segment_paths):
        """Updates the playlist.txt file with new segments."""
        with open(self.playlist_path, "w") as f:
            for path in segment_paths:
                # FFmpeg concat demuxer requires 'file' prefix and escaped paths
                f.write(f"file '{path.absolute()}'\n")
        logger.info(f"Updated playlist with {len(segment_paths)} segments.")

    def start_stream(self):
        """Starts the continuous FFmpeg stream."""
        if not RTMP_URL:
            logger.error("RTMP_URL not set. Cannot start stream.")
            return

        # FFmpeg command for continuous streaming from a concat list
        # -re: Read input at native frame rate
        # -f concat: Use concat demuxer
        # -safe 0: Allow absolute paths
        # -stream_loop -1: Loop the playlist (useful if we want to repeat fallback)
        
        cmd = [
            'ffmpeg', '-y',
            '-re',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(self.playlist_path),
            '-c', 'copy', # We assume segments are already encoded correctly in stitcher.py
            '-f', 'flv',
            RTMP_URL
        ]

        logger.info("Starting FFmpeg stream to YouTube...")
        try:
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            return self.process
        except Exception as e:
            logger.error(f"Failed to start stream: {e}")
            return None

    def monitor_stream(self):
        """Monitors the FFmpeg process and restarts if it fails."""
        if self.process and self.process.poll() is not None:
            logger.warning("Stream process died. Restarting...")
            return self.start_stream()
        return self.process

if __name__ == "__main__":
    s = Streamer()
    # s.start_stream()
