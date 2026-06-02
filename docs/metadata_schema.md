# metadata_schema.md

## Metadata Schema v1.0

Single Source of Truth cho toàn bộ hệ thống.

Mọi module phải tuân thủ schema này.

---

# Video

```json
{
  "video_id": "L01_V001",

  "video_path": "",

  "duration": 0.0,

  "fps": 30,

  "width": 1920,

  "height": 1080
}
```

---

# Segment

```json
{
  "segment_id": "SEG_000001",

  "video_id": "L01_V001",

  "start_time": 0.0,

  "end_time": 5.0,

  "duration": 5.0
}
```

---

# Keyframe

```json
{
  "frame_id": "FRAME_000001",

  "video_id": "L01_V001",

  "segment_id": "SEG_000001",

  "timestamp": 1.25,

  "frame_path": "",

  "thumbnail_path": ""
}
```

---

# Caption

```json
{
  "frame_id": "FRAME_000001",

  "caption": "a man standing near a red bus",

  "caption_model": "qwen2.5-vl"
}
```

---

# OCR

```json
{
  "frame_id": "FRAME_000001",

  "ocr_text": "McDonalds",

  "ocr_confidence": 0.95
}
```

---

# ASR

```json
{
  "segment_id": "SEG_000001",

  "transcript": "welcome to our store",

  "language": "en"
}
```

---

# Objects

```json
{
  "frame_id": "FRAME_000001",

  "objects": [
    {
      "label": "person",
      "confidence": 0.98
    },
    {
      "label": "bus",
      "confidence": 0.95
    }
  ]
}
```

---

# Embedding Metadata

```json
{
  "embedding_id": "EMB_000001",

  "frame_id": "FRAME_000001",

  "model_name": "siglip",

  "vector_dim": 768
}
```

---

# Unified Retrieval Record

Mọi retrieval module phải trả về format này.

```json
{
  "video_id": "",

  "segment_id": "",

  "frame_id": "",

  "timestamp": 0.0,

  "score": 0.0,

  "caption": "",

  "ocr_text": "",

  "objects": [],

  "thumbnail_url": "",

  "video_url": ""
}
```

---

# Folder Ownership

data/raw/
only ingestion team writes

data/keyframes/
only indexing team writes

data/metadata/
only metadata team writes

vector_db/
only indexing team writes

No team may overwrite another team's artifacts.
