import time
import threading
from loguru import logger
from generator import MusicGenerator
from visualizer import Visualizer
from stitcher import MediaStitcher
from streamer import Streamer
from config import QUEUE_MIN_SIZE, OUTPUT_DIR

class StreamManager:
    def __init__(self):
        self.generator = MusicGenerator()
        self.visualizer = Visualizer()
        self.stitcher = MediaStitcher()
        self.streamer = Streamer()
        
        self.segments_queue = []
        self.is_running = False

    def replenish_queue(self):
        """Ensures there are always enough segments ready to play."""
        current_segments = list((OUTPUT_DIR / "segments").glob("*.mp4"))
        
        while len(current_segments) < QUEUE_MIN_SIZE:
            logger.info(f"Queue low ({len(current_segments)}/{QUEUE_MIN_SIZE}). Generating new content...")
            
            # 1. Generate Audio
            audio_path = self.generator.generate_song()
            if not audio_path:
                logger.error("Failed to get audio. Skipping.")
                continue
                
            # 2. Get Video Background
            video_path = self.visualizer.get_background_video()
            
            # 3. Stitch
            track_name = audio_path.stem.replace("song_", "AI Chill #")
            timestamp = int(time.time())
            output_filename = f"segment_{timestamp}.mp4"
            
            segment_path = self.stitcher.stitch(audio_path, video_path, track_name, output_filename)
            
            if segment_path:
                current_segments.append(segment_path)
            else:
                logger.error("Failed to stitch segment.")
                
            time.sleep(1) # Small delay to avoid hammering APIs
            
        return current_segments

    def run(self):
        """Main loop to keep the stream alive 24/7."""
        self.is_running = True
        logger.info("Starting Stream Manager...")
        
        # Initial queue fill
        segments = self.replenish_queue()
        self.streamer.update_playlist(segments)
        
        # Start the stream
        self.streamer.start_stream()
        
        try:
            while self.is_running:
                # 1. Watchdog: Check if stream is still alive
                self.streamer.monitor_stream()
                
                # 2. Maintenance: Replenish queue in background
                # (In a production app, this would be a separate thread)
                self.replenish_queue()
                
                # 3. Update playlist with latest segments
                # Note: FFmpeg concat demuxer might need a restart or a different strategy 
                # for truly seamless live updates. For now, we update the file.
                current_segments = sorted(list((OUTPUT_DIR / "segments").glob("*.mp4")))
                self.streamer.update_playlist(current_segments)
                
                # Sleep and repeat
                time.sleep(30)
                
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            self.is_running = False
            if self.streamer.process:
                self.streamer.process.terminate()

if __name__ == "__main__":
    manager = StreamManager()
    manager.run()
