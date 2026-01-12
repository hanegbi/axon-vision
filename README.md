# Axon Vision - Video Analytics Pipeline

A multiprocessing video analytics pipeline with motion detection and optional blur feature.

### Flow

Video file goes to Streamer which reads frames, then Detector detects motion, finally Presenter displays results. Each process runs independently and communicates via bounded queues to prevent memory buildup.

## Architecture

![Pipeline Architecture](data/diagram.png)

## Installation

```bash
uv pip install -r requirements.txt
```

## Usage

```bash
python main.py --video path/to/video.mp4
python main.py --video path/to/video.mp4 --blur
```

## Packages

- **opencv-python**: Video capture, frame processing, and display
- **pydantic**: Message validation and serialization
- **numpy**: Array operations for frame data
- **black**: Code formatting (development)

## Examples

Example output on common surveillance camera data showing people walking.

**Without blur:**
![Display without blur](data/display_no_blur.png)

**With blur:**
![Display with blur](data/display_blur.png)
