# metadata_schema.md

## Metadata Schema v1.1

Single Source of Truth cho toàn bộ hệ thống.

Mọi module phải tuân thủ schema này.

> **Changelog v1.1**: Bổ sung `shot_id`, `frame_index`, `embedding_id`, `embedding_index`,
> `timestamp_source`, `timestamp_confidence` vào Keyframe schema.
> Chuẩn hóa `frame_map.json` là metadata chính cho retrieval.

---

# Video

```json
{
  "video_id": "L01_V001",
  "video_path": "data/raw/L01_V001.mp4",
  "duration": 120.0,
  "fps": 30,
  "width": 1920,
  "height": 1080
}
```

---

# Segment

```json
{
  "segment_id": "SEG_L01_V001_000001",
  "video_id": "L01_V001",
  "start_time": 0.0,
  "end_time": 5.0,
  "duration": 5.0
}
```

---

# Keyframe

`frame_map.json` là metadata chính — tất cả retrieval phải đọc từ đây.

```json
{
  "frame_id": "FRAME_L01_V001_000001",
  "video_id": "L01_V001",
  "shot_id": "SHOT_L01_V001_000001",
  "segment_id": "SEG_L01_V001_000001",
  "timestamp": 1.25,
  "timestamp_source": "video_fps",
  "timestamp_confidence": 1.0,
  "frame_index": 37,
  "keyframe_path": "data/keyframes/L01_V001/000001.jpg",
  "frame_path": "data/keyframes/L01_V001/000001.jpg",
  "thumbnail_path": "data/keyframes/L01_V001/000001.jpg",
  "embedding_id": "EMB_L01_V001_000001",
  "embedding_index": 0,
  "faiss_index": 0
}
```

### Trường bắt buộc (required)

| Trường | Kiểu | Mô tả |
|---|---|---|
| `frame_id` | str | ID duy nhất của keyframe, dạng `FRAME_{video_id}_{N:06d}` |
| `video_id` | str | ID video nguồn |
| `shot_id` | str | ID shot, dạng `SHOT_{video_id}_{N:06d}` |
| `segment_id` | str | ID segment, dạng `SEG_{video_id}_{N:06d}` |
| `timestamp` | float | Thời điểm (giây) trong video |
| `keyframe_path` | str | Đường dẫn file ảnh keyframe |
| `frame_path` | str | Alias của `keyframe_path` (backward compat) |
| `thumbnail_path` | str | Đường dẫn thumbnail (có thể trùng keyframe_path) |

### Trường bổ sung (optional nhưng khuyến nghị)

| Trường | Kiểu | Mô tả |
|---|---|---|
| `timestamp_source` | str | Cách tính timestamp: `"video_fps"` \| `"interval"` \| `"matched_frame"` |
| `timestamp_confidence` | float | Độ tin cậy timestamp: 1.0 = chắc chắn, 0.5 = ước tính |
| `frame_index` | int \| null | Frame index trong video gốc |
| `embedding_id` | str | ID của embedding tương ứng |
| `embedding_index` | int | Vị trí trong file `.npy` |
| `faiss_index` | int | Vị trí trong FAISS index (cùng thứ tự với embedding_index) |

### Giá trị `timestamp_source`

| Giá trị | Ý nghĩa |
|---|---|
| `"video_fps"` | Tính chính xác từ `frame_index / fps` (cao nhất) |
| `"matched_frame"` | Tính từ visual matching với video gốc |
| `"interval"` | Ước tính từ `(keyframe_number - 1) * interval_sec` |
| `"unknown"` | Không xác định được nguồn |

---

# Caption

```json
{
  "frame_id": "FRAME_L01_V001_000001",
  "caption": "a man standing near a red bus",
  "caption_model": "qwen2.5-vl"
}
```

---

# OCR

```json
{
  "frame_id": "FRAME_L01_V001_000001",
  "ocr_text": "McDonalds",
  "ocr_confidence": 0.95
}
```

---

# ASR

```json
{
  "segment_id": "SEG_L01_V001_000001",
  "transcript": "welcome to our store",
  "language": "en"
}
```

---

# Objects

```json
{
  "frame_id": "FRAME_L01_V001_000001",
  "objects": [
    { "label": "person", "confidence": 0.98 },
    { "label": "bus", "confidence": 0.95 }
  ]
}
```

---

# Embedding Metadata

```json
{
  "embedding_id": "EMB_L01_V001_000001",
  "frame_id": "FRAME_L01_V001_000001",
  "video_id": "L01_V001",
  "model_name": "openclip_vit_b16",
  "vector_dim": 512,
  "embedding_index": 0
}
```

---

# frame_map.json — Metadata chính cho retrieval

File `frame_map.json` là nguồn dữ liệu **bắt buộc** cho retrieval.
Key là `faiss_index` (string), value là keyframe record đầy đủ.

```json
{
  "0": {
    "frame_id": "FRAME_L01_V001_000001",
    "video_id": "L01_V001",
    "shot_id": "SHOT_L01_V001_000001",
    "segment_id": "SEG_L01_V001_000001",
    "timestamp": 1.25,
    "timestamp_source": "video_fps",
    "timestamp_confidence": 1.0,
    "frame_index": 37,
    "keyframe_path": "data/keyframes/L01_V001/000001.jpg",
    "thumbnail_path": "data/keyframes/L01_V001/000001.jpg",
    "embedding_id": "EMB_L01_V001_000001",
    "embedding_index": 0
  }
}
```

---

# Unified Retrieval Record

Mọi retrieval module phải trả về format này.

```json
{
  "video_id": "L01_V001",
  "segment_id": "SEG_L01_V001_000001",
  "frame_id": "FRAME_L01_V001_000001",
  "timestamp": 1.25,
  "timestamp_source": "video_fps",
  "score": 0.92,
  "caption": "a man standing near a red bus",
  "ocr_text": "McDonalds",
  "objects": ["person", "bus"],
  "thumbnail_url": "/static/keyframes/L01_V001/000001.jpg",
  "video_url": "/static/videos/L01_V001.mp4"
}
```

---

# Folder Ownership

| Folder | Owner | Quy tắc |
|---|---|---|
| `data/raw/` | P2 - Indexing | Chỉ indexing team writes |
| `data/keyframes/` | P2 - Indexing | Chỉ indexing team writes |
| `data/metadata/` | P3 - Metadata | Chỉ metadata team writes |
| `data/indexes/` | P2 - Indexing | Chỉ indexing team writes |

**Không team nào được phép overwrite artifact của team khác.**
