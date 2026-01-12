import argparse
import signal
from multiprocessing import Process, Queue, Event
from logging_utils import setup_logging, get_logger
from streamer import streamer_process
from detector import detector_process
from presenter import presenter_process

QUEUE_SIZE = 4


def main():
    parser = argparse.ArgumentParser(
        description="Axon Vision - Video analytics pipeline",
        epilog="Usage: python main.py --video video.mp4",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--video", required=True, help="Path to video file")
    parser.add_argument("--blur", action="store_true", help="Blur detections")
    args = parser.parse_args()

    log_queue = Queue()
    log_listener = setup_logging(log_queue)
    log_listener.start()

    logger = get_logger(__name__, log_queue)
    logger.info("Starting video analytics pipeline")
    logger.info(f"Video: {args.video}")

    frames_q = Queue(maxsize=QUEUE_SIZE)
    results_q = Queue(maxsize=QUEUE_SIZE)
    stop_event = Event()

    def signal_handler(_sig, _frame):
        stop_event.set()

    signal.signal(signal.SIGINT, signal_handler)

    streamer = Process(target=streamer_process, args=(args.video, frames_q, stop_event, log_queue), name="Streamer")

    detector = Process(target=detector_process, args=(frames_q, results_q, stop_event, log_queue), name="Detector")

    presenter = Process(target=presenter_process, args=(results_q, stop_event, log_queue, args.blur), name="Presenter")

    streamer.start()
    detector.start()
    presenter.start()

    try:
        streamer.join()
        detector.join()
        presenter.join()
    except KeyboardInterrupt:
        logger.info("Interrupted, shutting down")
        stop_event.set()
        streamer.join()
        detector.join()
        presenter.join()
    except Exception as e:
        logger.error(f"Pipeline error: {e}", exc_info=True)
        stop_event.set()
        streamer.join()
        detector.join()
        presenter.join()
    finally:
        log_listener.stop()
        logger.info("Pipeline finished")


if __name__ == "__main__":
    main()
