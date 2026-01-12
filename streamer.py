import cv2
import time
from messages import FrameMsg
from logging_utils import get_logger


class Streamer:
    """Reads frames from video and sends them to detector queue."""

    def __init__(self, video_path, frames_q, stop_event, log_queue):
        """Initialize Streamer.

        Args:
            video_path: Path to video file.
            frames_q: Queue to send FrameMsg objects.
            stop_event: Event to signal early shutdown.
            log_queue: Multiprocessing queue for log messages.
        """
        self.video_path = video_path
        self.frames_q = frames_q
        self.stop_event = stop_event
        self.log_queue = log_queue

    def run(self):
        """Run the streamer process."""
        logger = get_logger(__name__, self.log_queue)
        logger.info(f"Streamer starting, video: {self.video_path}")

        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            logger.error(f"Failed to open video: {self.video_path}")
            self.frames_q.put(None)
            return

        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = 30.0
        frame_delay = 1.0 / fps

        frame_id = 0
        start_time = time.time()

        try:
            while not self.stop_event.is_set():
                ret, frame = cap.read()

                if not ret:
                    logger.info("End of video stream")
                    break

                if self.stop_event.is_set():
                    break

                timestamp = time.time() - start_time

                msg = FrameMsg(frame_id=frame_id, timestamp=timestamp, frame=frame)

                self.frames_q.put(msg)
                frame_id += 1
                time.sleep(frame_delay)

        except Exception as e:
            logger.error(f"Streamer error: {e}", exc_info=True)

        finally:
            cap.release()
            self.frames_q.put(None)
            logger.info("Streamer finished")


def streamer_process(video_path, frames_q, stop_event, log_queue):
    """Process entry point for Streamer."""
    streamer = Streamer(video_path, frames_q, stop_event, log_queue)
    streamer.run()
