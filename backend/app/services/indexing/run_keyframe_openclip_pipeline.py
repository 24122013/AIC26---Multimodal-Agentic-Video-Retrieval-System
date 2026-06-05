from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import numpy as np

from build_openclip_index import choose_device, encode_keyframes, write_jsonl
from normalize_keyframe_metadata import (
    build_metadata_records,
    infer_video_id,
    write_jsonl as write_metadata_jsonl,
)
from validate_keyframes import validate_records


def write_json(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def set_model_cache(cache_dir: Path) -> None:
    cache_dir.mkdir(parents=True, exist_ok=True)
    hub_dir = cache_dir / "hub"
    hub_dir.mkdir(parents=True, exist_ok=True)
    os.environ["HF_HOME"] = cache_dir.as_posix()
    os.environ["HUGGINGFACE_HUB_CACHE"] = hub_dir.as_posix()


def default_paths(output_root: Path, video_id: str) -> dict[str, Path]:
    metadata_dir = output_root / "metadata"
    embeddings_dir = output_root / "embeddings"
    return {
        "metadata_path": metadata_dir / f"keyframes_{video_id}.jsonl",
        "validation_report_path": metadata_dir / f"keyframes_{video_id}_validation.json",
        "embeddings_path": embeddings_dir / f"openclip_vit_b16_{video_id}.npy",
        "embedding_metadata_path": metadata_dir / f"openclip_vit_b16_embeddings_{video_id}.jsonl",
        "skipped_path": metadata_dir / f"openclip_vit_b16_skipped_{video_id}.jsonl",
        "benchmark_path": metadata_dir / f"openclip_vit_b16_benchmark_{video_id}.json",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalize, validate, and encode one keyframe folder with OpenCLIP."
    )
    parser.add_argument(
        "--keyframe-dir",
        type=Path,
        required=True,
        help="Folder containing keyframe images for one video.",
    )
    parser.add_argument("--video-id", default=None)
    parser.add_argument("--output-root", type=Path, default=Path("data"))
    parser.add_argument("--timestamp-interval-sec", type=float, default=2.0)
    parser.add_argument("--min-width", type=int, default=16)
    parser.add_argument("--min-height", type=int, default=16)
    parser.add_argument("--model-name", default="ViT-B-16")
    parser.add_argument("--pretrained", default="laion2b_s34b_b88k")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--no-autocast", action="store_true")
    parser.add_argument(
        "--model-cache-dir",
        type=Path,
        default=Path("data/model_cache/openclip"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.keyframe_dir.exists():
        raise SystemExit(f"Keyframe directory does not exist: {args.keyframe_dir}")

    video_id = infer_video_id(args.keyframe_dir, args.video_id)
    paths = default_paths(args.output_root, video_id)
    set_model_cache(args.model_cache_dir)

    print(f"[1/3] Normalizing metadata for {video_id}")
    records = build_metadata_records(
        keyframe_dir=args.keyframe_dir,
        video_id=video_id,
        timestamp_interval_sec=args.timestamp_interval_sec,
    )
    if not records:
        raise SystemExit(f"No keyframe images found in: {args.keyframe_dir}")
    write_metadata_jsonl(records, paths["metadata_path"])
    print(f"      metadata: {paths['metadata_path']} ({len(records)} records)")

    print("[2/3] Validating keyframes")
    validation_report = validate_records(
        records=records,
        min_width=args.min_width,
        min_height=args.min_height,
    )
    write_json(validation_report, paths["validation_report_path"])
    print(
        f"      valid={validation_report['valid']} "
        f"errors={validation_report['error_count']} "
        f"report={paths['validation_report_path']}"
    )
    if not validation_report["valid"]:
        raise SystemExit("Validation failed. Fix keyframe metadata/images before encoding.")

    print("[3/3] Encoding OpenCLIP embeddings")
    device = choose_device(args.device)
    embeddings, embedding_records, skipped_records, benchmark = encode_keyframes(
        records=records,
        model_name=args.model_name,
        pretrained=args.pretrained,
        batch_size=args.batch_size,
        device=device,
        use_autocast=not args.no_autocast,
        model_cache_dir=args.model_cache_dir,
    )

    paths["embeddings_path"].parent.mkdir(parents=True, exist_ok=True)
    np.save(paths["embeddings_path"], embeddings)
    write_jsonl(embedding_records, paths["embedding_metadata_path"])
    write_jsonl(skipped_records, paths["skipped_path"])
    write_json(benchmark, paths["benchmark_path"])

    print(f"      embeddings: {paths['embeddings_path']} shape={embeddings.shape}")
    print(f"      embedding metadata: {paths['embedding_metadata_path']}")
    print(f"      skipped: {paths['skipped_path']} ({len(skipped_records)} records)")
    print(f"      benchmark: {paths['benchmark_path']}")


if __name__ == "__main__":
    main()
