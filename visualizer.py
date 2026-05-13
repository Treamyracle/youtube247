import cv2
import numpy as np
import librosa
import random
from pathlib import Path
from loguru import logger
from config import FALLBACK_VIDEO_DIR, STREAM_RESOLUTION

class Visualizer:
    def __init__(self):
        self.width, self.height = map(int, STREAM_RESOLUTION.split('x'))

    def get_background_video(self):
        """Returns a random looping video from the assets directory."""
        video_files = list(FALLBACK_VIDEO_DIR.glob("*.mp4")) + list(FALLBACK_VIDEO_DIR.glob("*.mov"))
        if not video_files:
            logger.warning("No background videos found in assets/videos. Using black background.")
            return None
        return random.choice(video_files)

    def create_waveform_frame(self, audio_segment, frame_idx, total_frames, background_img=None):
        """
        Creates a single frame with a waveform overlay.
        This is a simplified version; in production, we'd pre-calculate the waveform.
        """
        if background_img is None:
            frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        else:
            frame = background_img.copy()

        # Waveform logic (simplified)
        center_y = self.height // 2
        # Draw some reactive lines based on audio energy
        energy = np.mean(np.abs(audio_segment)) * 500
        cv2.line(frame, (self.width//4, center_y), (self.width*3//4, center_y), (255, 255, 255), 2)
        
        for i in range(100):
            x = int(self.width/4 + (i/100) * (self.width/2))
            h = int(energy * np.sin(frame_idx * 0.1 + i * 0.5))
            cv2.line(frame, (x, center_y - h), (x, center_y + h), (200, 200, 255), 1)

        return frame

    def generate_reactive_video(self, audio_path, output_path):
        """
        Generates a video with a reactive visualizer (placeholder for more complex logic).
        For 24/7 streams, it's often more efficient to use FFmpeg's 'showwaves' filter.
        """
        logger.info(f"Generating reactive visualizer for {audio_path}")
        # Implementation here would use FFmpeg filters via stitcher.py for better performance.
        pass

if __name__ == "__main__":
    viz = Visualizer()
    print(viz.get_background_video())
