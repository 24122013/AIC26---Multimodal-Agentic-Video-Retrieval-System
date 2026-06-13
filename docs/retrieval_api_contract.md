# Retrieval API Contract v0

Owner: P4 Retrieval

Phase 1 scope is visual text-to-keyframe retrieval only.

## Visual Search

Input:

```json
{
  "query": "a man cooking in a kitchen",
  "top_k": 20
}
```

Output:

```json
{
  "query": "a man cooking in a kitchen",
  "top_k": 20,
  "latency_ms": 123.4,
  "results": [
    {
      "video_id": "L01_V001",
      "frame_id": "FRAME_L01_V001_000001",
      "segment_id": "SEG_L01_V001_000001",
      "shot_id": "SHOT_L01_V001_000001",
      "timestamp": 1.25,
      "timestamp_source": "matched_frame",
      "timestamp_confidence": 0.9,
      "faiss_index": 0,
      "frame_index": 37,
      "score": 0.92,
      "keyframe_path": "data/keyframes/L01_V001/000001.jpg",
      "thumbnail_path": "data/keyframes/L01_V001/000001.jpg",
      "caption": "",
      "ocr_text": "",
      "objects": []
    }
  ]
}
```

## Runtime Inputs

The visual retrieval service expects these artifacts:

- FAISS index: `data/indexes/openclip_vit_b16_flat_ip.faiss`
- Frame map: `data/metadata/openclip_vit_b16_frame_map.json`
- OpenCLIP model: `ViT-B-16` with `laion2b_s34b_b88k`

These defaults can be overridden with environment variables:

- `RETRIEVAL_INDEX_PATH`
- `RETRIEVAL_FRAME_MAP_PATH`
- `RETRIEVAL_MODEL_NAME`
- `RETRIEVAL_PRETRAINED`
- `RETRIEVAL_DEVICE`
- `RETRIEVAL_MODEL_CACHE_DIR`
- `RETRIEVAL_DEFAULT_TOP_K`
- `RETRIEVAL_MAX_TOP_K`

## Definition of Done

- Empty query is rejected.
- `top_k` is clamped to `1..RETRIEVAL_MAX_TOP_K`.
- Invalid FAISS ids are skipped.
- Missing metadata records are skipped.
- Results always include `score`, `video_id`, `frame_id`, `timestamp`, and keyframe paths.
