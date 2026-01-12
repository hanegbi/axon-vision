import cv2
import time
from datetime import datetime
from logging_utils import get_logger

WINDOW_TITLE = "Axon Vision - Video Analytics"
WINDOW_SIZE = (960, 540)


class Presenter:
    """Displays frames with detections and time overlay."""

    def __init__(self, results_q, stop_event, log_queue, blur=False):
        """Initialize Presenter.

        Args:
            results_q: Queue to receive DetectMsg objects.
            stop_event: Event to signal shutdown (set on 'q' key).
            log_queue: Multiprocessing queue for log messages.
            blur: If True, blur is displayed.
        """
        self.results_q = results_q
        self.stop_event = stop_event
        self.log_queue = log_queue
        self.blur = blur

    def run(self):
        """Run the presenter process."""
        logger = get_logger(__name__, self.log_queue)
        logger.info("Presenter starting")
        if self.blur:
            logger.info("Blur enabled for detections")

        cv2.namedWindow(WINDOW_TITLE, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(WINDOW_TITLE, WINDOW_SIZE[0], WINDOW_SIZE[1])

        last_frame_time = None

        try:
            while not self.stop_event.is_set():
                detect_msg = self.results_q.get()

                if detect_msg is None:
                    logger.info("Presenter received sentinel")
                    break

                frame = detect_msg.frame.copy()
                frame_height, frame_width = frame.shape[:2]

                if self.blur:
                    for x, y, w, h in detect_msg.detections:
                        x1 = max(0, x)
                        y1 = max(0, y)
                        x2 = min(frame_width, x + w)
                        y2 = min(frame_height, y + h)

                        if x2 > x1 and y2 > y1:
                            roi = frame[y1:y2, x1:x2]
                            roi = cv2.GaussianBlur(roi, (21, 21), 0)
                            frame[y1:y2, x1:x2] = roi

                for x, y, w, h in detect_msg.detections:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cv2.putText(frame, current_time, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                cv2.imshow(WINDOW_TITLE, frame)

                if last_frame_time is not None:
                    elapsed = time.time() - last_frame_time
                    target_delay = 1.0 / 30.0
                    if elapsed < target_delay:
                        time.sleep(target_delay - elapsed)

                last_frame_time = time.time()

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    logger.info("Quit key pressed")
                    self.stop_event.set()
                    break

        except Exception as e:
            logger.error(f"Presenter error: {e}", exc_info=True)

        finally:
            cv2.destroyAllWindows()
            logger.info("Presenter finished")


def presenter_process(results_q, stop_event, log_queue, blur=False):
    """Process entry point for Presenter.

    Args:
        results_q: Queue to receive DetectMsg objects.
        stop_event: Event to signal shutdown.
        log_queue: Queue for logging.
        blur: If True, blur detections.
    """
    presenter = Presenter(results_q, stop_event, log_queue, blur)
    presenter.run()
