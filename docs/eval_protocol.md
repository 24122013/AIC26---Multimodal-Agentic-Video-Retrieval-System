# Evaluation Protocol v0

Owner: P1/P4

Phase 1 retrieval evaluation is intentionally small. The goal is to prove that
the baseline runs end-to-end before optimizing ranking quality.

## Metrics

- `Recall@K`: whether a known relevant video/frame appears in top K.
- `MRR`: reciprocal rank of the first relevant result.
- `Latency`: wall-clock query time in milliseconds.

## Baseline Query Set

Use 20-50 natural-language queries against the current subset. Each query should
store:

```json
{
  "query": "a man cooking in a kitchen",
  "relevant_video_id": "L01_V001",
  "relevant_frame_id": "FRAME_L01_V001_000123"
}
```

`relevant_frame_id` can be empty when only video-level ground truth is available.

## Phase 1 Pass Criteria

- Visual search returns top-k keyframes for every query.
- Average latency is reported.
- At least one Recall@K number is reported, even if the ground truth is rough.
- Failure cases are written down for the next iteration.
