from pydantic import BaseModel
import numpy


class FrameMsg(BaseModel):
    """Message of a video frame"""

    frame_id: int
    timestamp: float
    frame: numpy.ndarray

    class Config:
        arbitrary_types_allowed = True


class DetectMsg(BaseModel):
    """Message of a frame with motion detection results."""

    frame_id: int
    timestamp: float
    frame: numpy.ndarray
    detections: list[tuple[int, int, int, int]]

    class Config:
        arbitrary_types_allowed = True
