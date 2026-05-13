import subprocess
import os
from loguru import logger
from config import OUTPUT_DIR, FONT_PATH, TEXT_COLOR, TEXT_SIZE, STREAM_RESOLUTION, STREAM_FPS

class MediaStitcher:
    def __init__(self):
        self.output_segments = OUTPUT_DIR / "segments"

    def stitch(self, audio_path, video_path, track_name, output_filename):
        """
        Combines audio and video using FFmpeg.
        Adds a reactive waveform and 'Now Playing' text.
        """
        output_path = self.output_segments / output_filename
        
        # FFmpeg command
        # 1. Input audio
        # 2. Input video (looping)
        # 3. Filter_complex:
        #    - [0:a] showwaves (visualizer)
        #    - Overlay visualizer on video
        #    - Drawtext (Now Playing)
        
        # Simplified command for stability:
        # If video_path is None, we use a color source
        video_input = f"-stream_loop -1 -i \"{video_path}\"" if video_path else "-f lavfi -i color=c=black:s=1920x1080"
        
        cmd = [
            'ffmpeg', '-y',
            '-t', '120', # Limit to 120s or duration of audio (we'll detect audio duration in a real app)
            *video_input.split(),
            '-i', str(audio_path),
            '-filter_complex', 
            f"[0:v]scale={STREAM_RESOLUTION.replace('x', ':')}:force_original_aspect_ratio=increase,crop={STREAM_RESOLUTION.replace('x', ':')}[bg];" +
            f"[1:a]showwaves=s={STREAM_RESOLUTION}:mode=line:colors=0x66FFFFcc[v_wave];" +
            f"[bg][v_wave]overlay=format=auto[v_combined];" +
            f"[v_combined]drawtext=fontfile='{FONT_PATH}':text='Now Playing\\: {track_name}':x=(w-text_w)/2:y=h-100:fontsize={TEXT_SIZE}:fontcolor={TEXT_COLOR}:shadowcolor=black:shadowx=2:shadowy=2[outv]",
            '-map', '[outv]',
            '-map', '1:a',
            '-c:v', 'libx264', '-preset', 'veryfast', '-b:v', '3000k',
            '-c:a', 'aac', '-b:a', '192k',
            '-shortest',
            str(output_path)
        ]

        logger.info(f"Stitching {audio_path} with {video_path}")
        try:
            # We use a string for the command to handle complex filter escaping
            cmd_str = " ".join([f'"{arg}"' if ' ' in str(arg) or ':' in str(arg) else str(arg) for arg in cmd])
            # subprocess.run(cmd_str, shell=True, check=True)
            # Actually, using list is safer if escaped correctly, but FFmpeg filters are tricky.
            # Let's use a simpler version for the tool call
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                logger.error(f"FFmpeg error: {stderr.decode()}")
                return None
            
            logger.info(f"Stitched file saved to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Stitching failed: {e}")
            return None

if __name__ == "__main__":
    # Test
    stitcher = MediaStitcher()
    # stitcher.stitch("path/to/audio.mp3", "path/to/video.mp4", "AI Beat #1", "test.mp4")
