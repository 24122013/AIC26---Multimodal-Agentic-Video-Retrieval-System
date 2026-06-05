from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

try:
    from PIL import Image
except ImportError as exc:  # pragma: no cover - depends on local environment.
    raise SystemExit(
        "Pillow is required for keyframe validation. Install it with: "
        "pip install -r backend/requirements.txt"
    ) from exc


REQUIRED_FIELDS = {
    "frame_id",
    "video_id",
    "shot_id",
    "segment_id",
    "timestamp",
    "keyframe_path",
    "frame_path",
    "thumbnail_path",
}


def load_jsonl(path: Path) -> list[dict]:
    records = []
    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                records.append(
                    {
                        "_invalid_json": True,
                        "_line_number": line_number,
                        "_error": str(exc),
                    }
                )
                continue
            record["_line_number"] = line_number
            records.append(record)
    return records


def validate_image(path: Path, min_width: int, min_height: int) -> tuple[bool, dict]:
    if not path.exists():
        return False, {"error": "missing_file"}
    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            width, height = image.size
    except Exception as exc:  # noqa: BLE001 - validation should report all image failures.
        return False, {"error": "invalid_image", "detail": str(exc)}

    if width < min_width or height < min_height:
        return False, {"error": "image_too_small", "width": width, "height": height}

    return True, {"width": width, "height": height}


def validate_records(
    records: list[dict],
    min_width: int,
    min_height: int,
) -> dict:
    errors = []
    frame_ids = Counter(
        record.get("frame_id")
        for record in records
        if record.get("frame_id")
    )
    duplicate_ids = {frame_id for frame_id, count in frame_ids.items() if count > 1}
    image_sizes = Counter()

    for record in records:
        line_number = record.get("_line_number")
        if record.get("_invalid_json"):
            errors.append(
                {
                    "line_number": line_number,
                    "error": "invalid_json",
                    "detail": record.get("_error"),
                }
            )
            continue

        missing_fields = sorted(field for field in REQUIRED_FIELDS if field not in record)
        empty_fields = sorted(
            field
            for field in REQUIRED_FIELDS
            if field in record and record[field] in ("", None)
        )
        if missing_fields or empty_fields:
            errors.append(
                {
                    "line_number": line_number,
                    "frame_id": record.get("frame_id"),
                    "error": "schema_error",
                    "missing_fields": missing_fields,
                    "empty_fields": empty_fields,
                }
            )

        if record.get("frame_id") in duplicate_ids:
            errors.append(
                {
                    "line_number": line_number,
                    "frame_id": record.get("frame_id"),
                    "error": "duplicate_frame_id",
                }
            )

        keyframe_path = record.get("keyframe_path") or record.get("frame_path")
        if not keyframe_path:
            continue

        ok, image_info = validate_image(
            Path(keyframe_path),
            min_width=min_width,
            min_height=min_height,
        )
        if not ok:
            errors.append(
                {
                    "line_number": line_number,
                    "frame_id": record.get("frame_id"),
                    **image_info,
                }
            )
        else:
            image_sizes[f"{image_info['width']}x{image_info['height']}"] += 1

    return {
        "record_count": len(records),
        "valid": not errors,
        "error_count": len(errors),
        "errors": errors[:200],
        "duplicate_frame_id_count": len(duplicate_ids),
        "image_size_counts": dict(sorted(image_sizes.items())),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate keyframe metadata and images.")
    parser.add_argument(
        "--metadata-path",
        type=Path,
        default=Path("data/metadata/keyframes_L26_V200.jsonl"),
    )
    parser.add_argument(
        "--report-path",
        type=Path,
        default=Path("data/metadata/keyframes_L26_V200_validation.json"),
    )
    parser.add_argument("--min-width", type=int, default=16)
    parser.add_argument("--min-height", type=int, default=16)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.metadata_path.exists():
        raise SystemExit(f"Metadata file does not exist: {args.metadata_path}")

    records = load_jsonl(args.metadata_path)
    report = validate_records(
        records=records,
        min_width=args.min_width,
        min_height=args.min_height,
    )
    args.report_path.parent.mkdir(parents=True, exist_ok=True)
    with args.report_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)

    print(f"Validated {report['record_count']} records")
    print(f"Valid: {report['valid']} | errors: {report['error_count']}")
    print(f"Wrote report: {args.report_path}")
    if not report["valid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
