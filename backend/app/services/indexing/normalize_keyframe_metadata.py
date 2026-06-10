from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    import cv2
    import numpy as np
except ImportError:
    cv2 = None
    np = None


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def iter_keyframe_paths(keyframe_dir: Path) -> list[Path]:
    return sorted(
        path
        for path in keyframe_dir.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )


def infer_video_id(keyframe_dir: Path, video_id: str | None) -> str:
    if video_id:
        return video_id
    return keyframe_dir.name


def parse_keyframe_number(path: Path, fallback_index: int) -> int:
    try:
        return int(path.stem)
    except ValueError:
        return fallback_index


def read_video_info(video_path: Path) -> tuple[float, int]:
    if cv2 is None:
        raise SystemExit(
            "OpenCV is required when using --video-path. Install dependencies first."
        )

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    cap.release()

    if fps <= 0:
        raise ValueError(f"Cannot read FPS from video: {video_path}")
    if frame_count <= 0:
        raise ValueError(f"Cannot read frame count from video: {video_path}")

    return fps, frame_count


def image_to_small_array(path: Path, size: tuple[int, int]) -> np.ndarray:
    image = cv2.imread(str(path))
    if image is None:
        raise ValueError(f"Cannot read keyframe image: {path}")
    image = cv2.resize(image, size, interpolation=cv2.INTER_AREA)
    return image.astype(np.float32)


def mse(left: np.ndarray, right: np.ndarray) -> float:
    return float(np.mean((left - right) ** 2))


def match_keyframes_to_video(
    keyframe_paths: list[Path],
    video_path: Path,
    search_window_sec: float,
    resize_width: int,
    resize_height: int,
) -> dict[Path, int]:
    if cv2 is None or np is None:
        raise SystemExit(
            "OpenCV and NumPy are required when using --video-path. Install dependencies first."
        )

    fps, frame_count = read_video_info(video_path)
    window_frames = max(1, int(round(search_window_sec * fps)))
    resize_size = (resize_width, resize_height)
    keyframes = [
        (path, image_to_small_array(path, resize_size))
        for path in keyframe_paths
    ]
    matches: dict[Path, int] = {}
    previous_match = 0

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    for index, (keyframe_path, keyframe_image) in enumerate(keyframes, start=1):
        start_frame = 0 if index == 1 else previous_match
        end_frame = min(frame_count - 1, start_frame + window_frames)
        best_frame_index = start_frame
        best_score = float("inf")

        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        current_frame = start_frame
        while current_frame <= end_frame:
            ok, frame = cap.read()
            if not ok:
                break

            frame = cv2.resize(frame, resize_size, interpolation=cv2.INTER_AREA)
            score = mse(keyframe_image, frame.astype(np.float32))
            if score < best_score:
                best_score = score
                best_frame_index = current_frame

            current_frame += 1

        matches[keyframe_path] = best_frame_index
        previous_match = best_frame_index
        print(
            f"Matched {keyframe_path.name}: frame_index={best_frame_index} "
            f"timestamp={best_frame_index / fps:.3f}s mse={best_score:.2f}"
        )

    cap.release()
    return matches


def build_metadata_records(
    keyframe_dir: Path,
    video_id: str,
    timestamp_interval_sec: float,
    video_path: Path | None = None,
    search_window_sec: float = 12.0,
    resize_width: int = 160,
    resize_height: int = 90,
) -> list[dict]:
    records = []
    keyframe_paths = iter_keyframe_paths(keyframe_dir)
    fps = None
    frame_index_by_path: dict[Path, int] = {}
    if video_path is not None:
        fps, _ = read_video_info(video_path)
        frame_index_by_path = match_keyframes_to_video(
            keyframe_paths=keyframe_paths,
            video_path=video_path,
            search_window_sec=search_window_sec,
            resize_width=resize_width,
            resize_height=resize_height,
        )

    for fallback_index, path in enumerate(keyframe_paths, start=1):
        keyframe_number = parse_keyframe_number(path, fallback_index)
        frame_id = f"FRAME_{video_id}_{keyframe_number:06d}"
        shot_id = f"SHOT_{video_id}_{keyframe_number:06d}"
        segment_id = f"SEG_{video_id}_{keyframe_number:06d}"
        frame_index = frame_index_by_path.get(path)
        timestamp = (
            round(frame_index / fps, 3)
            if frame_index is not None and fps is not None
            else round((keyframe_number - 1) * timestamp_interval_sec, 3)
        )
        timestamp_source = "matched_frame" if frame_index is not None else "interval"
        timestamp_confidence = 0.9 if frame_index is not None else 0.5
        normalized_path = path.as_posix()

        records.append(
            {
                "frame_id": frame_id,
                "video_id": video_id,
                "shot_id": shot_id,
                "segment_id": segment_id,
                "timestamp": timestamp,
                "timestamp_source": timestamp_source,
                "timestamp_confidence": timestamp_confidence,
                "frame_index": frame_index,
                "keyframe_path": normalized_path,
                "frame_path": normalized_path,
                "thumbnail_path": normalized_path,
            }
        )
    return records


def write_jsonl(records: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create normalized keyframe metadata from an existing keyframe folder."
    )
    parser.add_argument(
        "--keyframe-dir",
        type=Path,
        default=Path("data/keyframes/keyframes/L26_V200"),
    )
    parser.add_argument("--video-id", default=None)
    parser.add_argument(
        "--output-path",
        type=Path,
        default=Path("data/metadata/keyframes_L26_V200.jsonl"),
    )
    parser.add_argument("--timestamp-interval-sec", type=float, default=2.0)
    parser.add_argument(
        "--video-path",
        type=Path,
        default=None,
        help="Optional source video. If provided, timestamp is computed as matched frame_index / video fps.",
    )
    parser.add_argument("--search-window-sec", type=float, default=12.0)
    parser.add_argument("--match-resize-width", type=int, default=160)
    parser.add_argument("--match-resize-height", type=int, default=90)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.keyframe_dir.exists():
        raise SystemExit(f"Keyframe directory does not exist: {args.keyframe_dir}")

    video_id = infer_video_id(args.keyframe_dir, args.video_id)
    records = build_metadata_records(
        keyframe_dir=args.keyframe_dir,
        video_id=video_id,
        timestamp_interval_sec=args.timestamp_interval_sec,
        video_path=args.video_path,
        search_window_sec=args.search_window_sec,
        resize_width=args.match_resize_width,
        resize_height=args.match_resize_height,
    )
    if not records:
        raise SystemExit(f"No keyframe images found in: {args.keyframe_dir}")

    write_jsonl(records, args.output_path)
    print(f"Wrote {len(records)} records to {args.output_path}")


if __name__ == "__main__":
    main()
