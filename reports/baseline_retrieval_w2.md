# Baseline Retrieval W2

Owner: P4 Retrieval

## Status

Implemented the Phase 1 visual retrieval path:

```text
text query -> OpenCLIP text embedding -> FAISS top-k -> frame_map lookup -> ranked keyframes
```

Code entry points:

- `backend/app/services/retrieval/search_visual.py`
- `backend/app/services/retrieval/retrieval_manager.py`
- `backend/app/api/retrieval.py`
- `backend/app/api/search.py`
- `backend/app/models/retrieval.py`

## How to Run

The service expects these default artifacts:

```text
data/indexes/openclip_vit_b16_flat_ip.faiss
data/metadata/openclip_vit_b16_frame_map.json
```

If paths differ, set:

```text
RETRIEVAL_INDEX_PATH
RETRIEVAL_FRAME_MAP_PATH
```

Python wrapper:

```python
from backend.app.services.retrieval.retrieval_manager import search_visual

response = search_visual("a man cooking in a kitchen", top_k=20)
print(response.to_dict())
```

## Verification

Automated tests cover:

- Query vector normalization.
- FAISS index result mapping to metadata records.
- Invalid FAISS ids are skipped.
- Output includes `score`, `video_id`, `frame_id`, `timestamp`, and keyframe paths.

Command used:

```powershell
& 'C:\Users\joovn\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m unittest backend.tests.test_search_visual
```

Result:

```text
Ran 2 tests
OK
```

## Current Blockers

The repo does not currently contain the real runtime artifacts, so live model
retrieval could not be benchmarked yet:

- No real FAISS index under `data/indexes/`.
- No real `openclip_vit_b16_frame_map.json` under `data/metadata/`.
- No 20-50 query sample file with ground truth.

## Next Retrieval Tasks

- Run live search after P2/P3 publish FAISS index and frame map.
- Record latency for 20-50 queries.
- Add `Recall@K` and `MRR` once ground truth is available.
- Extend visual-only baseline into hybrid search after caption/OCR artifacts exist.
