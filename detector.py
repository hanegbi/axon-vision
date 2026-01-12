import cv2
import imutils
from messages import DetectMsg
from logging_utils import get_logger

MIN_AREA = 500


class Detector:
    """Detects motion in frames and sends detection results."""

    def __init__(self, frames_q, results_q, stop_event, log_queue):
        """Initialize Detector.

        Args:
            frames_q: Queue to receive FrameMsg objects.
            results_q: Queue to send DetectMsg objects.
            stop_event: Event to signal early shutdown.
            log_queue: Queue for logging.
        """
        self.frames_q = frames_q
        self.results_q = results_q
        self.stop_event = stop_event
        self.log_queue = log_queue
        self.prev_frame = None

    def run(self):
        """Run the detector process."""
        logger = get_logger(__name__, self.log_queue)
        logger.info("Detector starting")

        try:
            while not self.stop_event.is_set():
                frame_msg = self.frames_q.get()

                if frame_msg is None:
                    logger.info("Detector received end signal, forwarding to presenter")
                    self.results_q.put(None)
                    break

                if self.stop_event.is_set():
                    self.results_q.put(None)
                    break

                gray_frame = cv2.cvtColor(frame_msg.frame, cv2.COLOR_BGR2GRAY)

                if self.prev_frame is None:
                    detections = []
                    self.prev_frame = gray_frame
                else:
                    diff = cv2.absdiff(gray_frame, self.prev_frame)
                    thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
                    thresh = cv2.dilate(thresh, None, iterations=2)
                    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    cnts = imutils.grab_contours(cnts)

                    detections = []
                    for c in cnts:
                        area = cv2.contourArea(c)
                        if area < MIN_AREA:
                            continue

                        x, y, w, h = cv2.boundingRect(c)
                        detections.append((x, y, w, h))

                    self.prev_frame = gray_frame

                detect_msg = DetectMsg(
                    frame_id=frame_msg.frame_id,
                    timestamp=frame_msg.timestamp,
                    frame=frame_msg.frame.copy(),
                    detections=detections,
                )

                self.results_q.put(detect_msg)

        except Exception as e:
            logger.error(f"Detector error: {e}", exc_info=True)
            self.results_q.put(None)

        finally:
            logger.info("Detector finished")


def detector_process(frames_q, results_q, stop_event, log_queue):
    """Process entry point for Detector."""
    detector = Detector(frames_q, results_q, stop_event, log_queue)
    detector.run()
