# Contributing Guide

Tài liệu này dành cho tất cả thành viên nhóm. Đọc kỹ trước khi bắt đầu làm việc.

---

## 1. Coding Convention

### Python style

- Formatter: **black** (line length 100)
- Linter: **ruff**
- Type hints: bắt buộc với tất cả function public
- Docstring: Google style

```python
def search_visual(query: str, top_k: int = 50) -> list[SearchResult]:
    """Search keyframes bằng text query thông qua CLIP embedding.

    Args:
        query: Text query từ người dùng.
        top_k: Số lượng kết quả trả về.

    Returns:
        Danh sách SearchResult đã sắp xếp theo score giảm dần.

    Raises:
        IndexNotReadyError: Nếu vector index chưa được build.
    """
    ...
```

### Import order

```python
# 1. Standard library
import os
import json
from pathlib import Path

# 2. Third-party
import numpy as np
import torch
from PIL import Image

# 3. Internal
from src.common.types import SearchResult
from src.common.config import Config
```

### Naming

| Loại | Convention | Ví dụ |
|------|-----------|-------|
| File | snake_case | `build_clip_index.py` |
| Class | PascalCase | `VectorDB`, `HybridSearcher` |
| Function/var | snake_case | `search_visual`, `top_k` |
| Constant | UPPER_SNAKE | `DEFAULT_TOP_K = 50` |
| Config key | snake_case | `embedding_dim: 512` |

---

## 2. Branch Convention

```
main          ← production-ready, KHÔNG push trực tiếp
develop       ← integration, merge từ feature branches
p1/...        ← P1 (Lead/System/Eval)
p2/...        ← P2 (Indexing)
p3/...        ← P3 (Metadata)
p4/...        ← P4 (Retrieval)
p5/...        ← P5 (Agent/UI)
hotfix/...    ← fix khẩn, base từ main
```

### Ví dụ tên branch

```bash
git checkout -b p2/clip-index-baseline
git checkout -b p3/add-ocr-pipeline
git checkout -b p4/hybrid-search-v1
git checkout -b p1/eval-metrics
```

---

## 3. Commit Message Format

Dùng Conventional Commits:

```
<type>(<scope>): <mô tả ngắn>

[body tùy chọn]
```

### Types

| Type | Khi nào dùng |
|------|-------------|
| `feat` | Thêm feature mới |
| `fix` | Sửa bug |
| `bench` | Thêm/cập nhật benchmark |
| `refactor` | Refactor không thay đổi behavior |
| `docs` | Cập nhật tài liệu |
| `test` | Thêm/sửa tests |
| `chore` | Cập nhật deps, config |
| `exp` | Thêm experiment/notebook |

### Ví dụ

```bash
feat(ingestion): add extract_keyframes with interval config
fix(retrieval): fix score normalization in hybrid search
bench(indexing): add CLIP vs SigLIP comparison table
docs(api): update retrieval_api_contract with new fields
exp(notebooks): add embedding dimension analysis
```

---

## 4. Pull Request Workflow

### Tạo PR

1. Push branch lên remote
2. Mở PR vào `develop` (KHÔNG vào `main` trực tiếp)
3. Điền đầy đủ PR template
4. Tag **@P1** (Tech Lead) để review

### PR Template

```markdown
## Mô tả
<!-- Tóm tắt ngắn những gì PR này làm -->

## Loại thay đổi
- [ ] feat: Feature mới
- [ ] fix: Bug fix
- [ ] bench: Benchmark/experiment
- [ ] docs: Tài liệu
- [ ] refactor: Refactor

## Module bị ảnh hưởng
- [ ] ingestion
- [ ] indexing
- [ ] retrieval
- [ ] agent
- [ ] eval
- [ ] ui
- [ ] common/types (⚠️ cần P1 review kỹ)

## Checklist schema & API
- [ ] Output đúng schema đã định nghĩa trong `docs/system/metadata_schema.md`
- [ ] Response format khớp `docs/api/retrieval_api_contract.md`
- [ ] Không break import của module khác

## Checklist chất lượng
- [ ] Đã chạy `black` và `ruff`
- [ ] Đã thêm type hints
- [ ] Đã thêm docstring
- [ ] Có sample output hoặc log

## Benchmark / Evidence
<!-- Link kết quả nếu có, hoặc paste bảng benchmark -->

## Cách test
<!-- Mô tả ngắn cách reviewer có thể test PR này -->
```

### Review checklist (P1)

Khi review PR, P1 kiểm tra:

- [ ] Schema output khớp `metadata_schema.md`
- [ ] API response khớp `retrieval_api_contract.md`
- [ ] Không import circular giữa modules
- [ ] Config thay đổi có cập nhật YAML sample chưa
- [ ] Có benchmark nếu là module quan trọng

---

## 5. Definition of Done

### Script ingestion

- [ ] Có CLI chạy được (`python run_caption.py --help`)
- [ ] Có config input/output rõ ràng
- [ ] Output đúng schema (`metadata_schema.md`)
- [ ] Có sample output trong `data/metadata/` (gitignored)
- [ ] Có log runtime
- [ ] Có hướng dẫn chạy trong module README

### Retrieval module

- [ ] Có function/API rõ ràng với type hints
- [ ] Trả về đúng `SearchResult` format
- [ ] Có test với ≥5 query mẫu
- [ ] Có đo latency
- [ ] Có benchmark Recall@K nếu có ground truth

### UI feature

- [ ] Dùng được trong mock contest không cần chỉnh code
- [ ] Có log interaction
- [ ] Không làm vỡ flow search hiện tại
- [ ] Đã test trên ít nhất 10 query thực tế

### Experiment / Ablation

- [ ] Có config YAML rõ ràng
- [ ] Có script để chạy lại
- [ ] Có bảng kết quả số liệu
- [ ] Có nhận xét ngắn
- [ ] Có lưu log/artifact tại `reports/`

---

## 6. Quy tắc về data

- **KHÔNG BAO GIỜ** commit raw video lên git
- **KHÔNG BAO GIỜ** commit file embedding lớn (`.npy`, `.faiss`, `.bin`)
- `data/raw/`, `data/embeddings/`, `logs/` đều gitignored
- Metadata nhỏ (`.jsonl` mẫu ≤ 1MB) có thể commit để làm example

---

## 7. Standup & Meeting

### Daily standup (15 phút)

Mỗi người trả lời 3 câu:
1. Hôm qua làm gì?
2. Hôm nay làm gì?
3. Đang bị block ở đâu?

### Weekly (cuối tuần)

1. Tạo `reports/weekly/week-XX-PX.md` theo template
2. Demo kỹ thuật những gì đã làm
3. Benchmark review
4. Planning tuần sau

### Từ tuần 8

2 mock contest/tuần + error analysis sau mỗi buổi.
