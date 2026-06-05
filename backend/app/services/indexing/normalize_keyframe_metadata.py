from __future__ import annotations

import argparse
import json
from pathlib import Path


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


def build_metadata_records(
    keyframe_dir: Path,
    video_id: str,
    timestamp_interval_sec: float,
) -> list[dict]:
    records = []
    for fallback_index, path in enumerate(iter_keyframe_paths(keyframe_dir), start=1):
        keyframe_number = parse_keyframe_number(path, fallback_index)
        frame_id = f"FRAME_{video_id}_{keyframe_number:06d}"
        shot_id = f"SHOT_{video_id}_{keyframe_number:06d}"
        segment_id = f"SEG_{video_id}_{keyframe_number:06d}"
        timestamp = round((keyframe_number - 1) * timestamp_interval_sec, 3)
        normalized_path = path.as_posix()

        records.append(
            {
                "frame_id": frame_id,
                "video_id": video_id,
                "shot_id": shot_id,
                "segment_id": segment_id,
                "timestamp": timestamp,
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
    )
    if not records:
        raise SystemExit(f"No keyframe images found in: {args.keyframe_dir}")

    write_jsonl(records, args.output_path)
    print(f"Wrote {len(records)} records to {args.output_path}")


if __name__ == "__main__":
    main()
