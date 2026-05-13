from manager import StreamManager
from loguru import logger
import sys

def main():
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    logger.add("logs/main.log", rotation="50 MB", level="DEBUG")

    logger.info("=========================================")
    logger.info("   24/7 AI MUSIC LIVESTREAM STARTED     ")
    logger.info("=========================================")
    
    try:
        manager = StreamManager()
        manager.run()
    except Exception as e:
        logger.critical(f"Main loop crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
