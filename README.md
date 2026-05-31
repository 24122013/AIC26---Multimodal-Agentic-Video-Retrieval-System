# 🏆 HCMC AI Challenge 2026 — AIO_DataDominator

> **Multimodal Agentic Video Retrieval System**  
> Hệ thống truy xuất video đa phương thức với agent hỗ trợ query decomposition, hybrid indexing, temporal reranking và UI tương tác.

---

## 📋 Mục lục

- [Tổng quan dự án](#tổng-quan-dự-án)
- [Kiến trúc hệ thống](#kiến-trúc-hệ-thống)
- [Cấu trúc repo](#cấu-trúc-repo)
- [Phân công team](#phân-công-team)
- [Roadmap 12 tuần](#roadmap-12-tuần)
- [Cài đặt](#cài-đặt)
- [Cách sử dụng](#cách-sử-dụng)
- [Quy trình làm việc](#quy-trình-làm-việc)
- [Tài liệu kỹ thuật](#tài-liệu-kỹ-thuật)
- [Kết quả & Benchmark](#kết-quả--benchmark)
- [Contributing](#contributing)

---

## Tổng quan dự án

### Bài toán

Xây dựng hệ thống truy xuất multimedia hỗ trợ các task của AI Challenge:

| Task | Mô tả |
|------|-------|
| **AVS** | Ad-hoc Video Search — tìm video theo mô tả tự do |
| **KIS** | Known-Item Search — tìm đúng một item theo gợi ý |
| **KISV** | Known-Item Search with Visual Query — tìm bằng query hình ảnh |
| **KIST** | Known-Item Search with Textual Hints — tìm bằng gợi ý văn bản |
| **KISC** | Known-Item Search with Interactive Conversation — tìm qua hội thoại |
| **QA/VQA** | Trả lời câu hỏi dựa trên dữ liệu multimedia |

### Mục tiêu kép

1. **Thi đấu:** Xây dựng hệ thống có khả năng cạnh tranh cao tại AI Challenge 2026.
2. **Paper:** Tạo đủ kết quả thực nghiệm, benchmark và ablation để viết system paper.

### Nguyên tắc cốt lõi

```
Baseline trước → Benchmark sau → Tối ưu có kiểm chứng → Viết paper từ ablation
```

---

## Kiến trúc hệ thống

```
Video Dataset
     │
     ▼
┌─────────────────────────────┐
│  Segment / Keyframe Extract │  ← P2: extract_keyframes.py
└─────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────┐
│              Multimodal Indexing                    │
│  - CLIP / SigLIP / OpenCLIP embedding  (P2)        │
│  - Caption (BLIP/LLaVA/Qwen2.5-VL)    (P3)        │
│  - OCR (PaddleOCR / EasyOCR)           (P3)        │
│  - ASR (Whisper / faster-whisper)      (P3)        │
│  - Object Detection (YOLO-World)       (P3)        │
│  - Temporal metadata                   (P2/P3)     │
└─────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────┐
│              Retrieval Engine                       │
│  - Vector search (FAISS/Qdrant)        (P4)        │
│  - Text search (BM25)                  (P4)        │
│  - Hybrid search                       (P4)        │
│  - Re-ranking (cross-encoder/VLM)      (P4)        │
│  - Temporal search                     (P4)        │
└─────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────┐
│              Agent / Tool Layer                     │
│  - Query rewriting & decomposition     (P5)        │
│  - Tool calling                        (P5)        │
│  - Vietnamese ↔ English expansion      (P5)        │
│  - Result explanation                  (P5)        │
└─────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────┐
│              Competition UI                         │
│  - Search box & result grid            (P5)        │
│  - Timeline & neighbor frames          (P5)        │
│  - Candidate basket                    (P5)        │
│  - Submit result + interaction log     (P5)        │
└─────────────────────────────────────────────────────┘
```

---

## Cấu trúc repo

```
hcmc-ai-challenge/
│
├── README.md                    # File này
├── CONTRIBUTING.md              # Hướng dẫn đóng góp, branch convention
├── CHANGELOG.md                 # Lịch sử thay đổi lớn
├── .gitignore
├── requirements.txt             # Python dependencies
├── pyproject.toml               # Package config
│
├── configs/                     # Tất cả cấu hình YAML
│   ├── indexing.yaml            # Cấu hình ingestion & embedding
│   ├── retrieval.yaml           # Hybrid search weights
│   ├── models.yaml              # Model paths & params
│   └── eval.yaml                # Evaluation config
│
├── data/                        # ⚠️ KHÔNG commit data thật lên git
│   ├── raw/                     # Video gốc (symlink hoặc mount)
│   ├── keyframes/               # Frame đã extract
│   ├── segments/                # Segment metadata
│   ├── metadata/                # .jsonl / .parquet output
│   │   ├── keyframes.jsonl
│   │   ├── captions.jsonl
│   │   ├── ocr.jsonl
│   │   ├── asr.jsonl
│   │   └── objects.jsonl
│   ├── queries/                 # Query mẫu & ground truth
│   │   ├── sample_queries.jsonl
│   │   └── ground_truth.jsonl
│   └── embeddings/              # Vector cache (large, gitignored)
│
├── src/                         # Source code chính
│   ├── common/                  # Shared utilities
│   │   ├── __init__.py
│   │   ├── metadata_store.py    # P3: Loader metadata dùng chung
│   │   ├── types.py             # P4: Shared type definitions
│   │   └── config.py            # Config loader
│   │
│   ├── ingestion/               # P2 & P3: Extract & enrich
│   │   ├── __init__.py
│   │   ├── extract_keyframes.py # P2: ffmpeg/OpenCV keyframe
│   │   ├── extract_segments.py  # P2: Shot/segment boundary
│   │   ├── run_caption.py       # P3: BLIP/LLaVA captioning
│   │   ├── run_ocr.py           # P3: PaddleOCR / EasyOCR
│   │   ├── run_asr.py           # P3: Whisper ASR
│   │   ├── run_object_detection.py  # P3: YOLO-World
│   │   └── README.md            # Hướng dẫn module ingestion
│   │
│   ├── indexing/                # P2: Build vector index
│   │   ├── __init__.py
│   │   ├── build_clip_index.py  # P2: Encode CLIP/SigLIP/OpenCLIP
│   │   ├── build_text_index.py  # P4: BM25 for caption/OCR/ASR
│   │   ├── vector_db.py         # P2: FAISS/Qdrant interface
│   │   └── README.md
│   │
│   ├── retrieval/               # P4: Search & ranking
│   │   ├── __init__.py
│   │   ├── search_visual.py     # P4: Text → embedding → vector search
│   │   ├── search_text.py       # P4: BM25 text search
│   │   ├── hybrid_search.py     # P4: Combine visual + text
│   │   ├── rerank.py            # P4: Cross-encoder / VLM rerank
│   │   ├── temporal_search.py   # P4: Multi-event temporal query
│   │   ├── types.py             # SearchResult, SearchQuery types
│   │   └── README.md
│   │
│   ├── agent/                   # P5: Query understanding & tool calling
│   │   ├── __init__.py
│   │   ├── planner.py           # P5: Query decomposition & planning
│   │   ├── tools.py             # P5: Tool definitions
│   │   ├── prompts.py           # P5: LLM prompt templates
│   │   ├── query_expansion.py   # P5: Vi/En expansion
│   │   └── README.md
│   │
│   ├── eval/                    # P1: Evaluation & benchmarking
│   │   ├── __init__.py
│   │   ├── metrics.py           # P1: Recall@K, MRR, latency
│   │   ├── benchmark.py         # P1: Run eval on query set
│   │   ├── ablation.py          # P1: Multi-config ablation runner
│   │   └── README.md
│   │
│   └── ui/                      # P5: Streamlit / FastAPI UI
│       ├── app.py               # P5: Main UI entry point
│       ├── components/          # P5: Reusable UI components
│       └── README.md
│
├── scripts/                     # Shell scripts pipeline
│   ├── setup.sh                 # Cài đặt môi trường
│   ├── run_ingest.sh            # Chạy full ingestion pipeline
│   ├── run_index.sh             # Build index
│   ├── run_baseline.sh          # P1: End-to-end baseline
│   ├── run_eval.sh              # Chạy evaluation
│   └── run_ablation.sh          # Chạy ablation experiments
│
├── configs/
│   ├── indexing.yaml
│   ├── retrieval.yaml
│   ├── models.yaml
│   └── eval.yaml
│
├── tests/                       # Unit & integration tests
│   ├── test_ingestion.py
│   ├── test_retrieval.py
│   ├── test_eval.py
│   └── test_agent.py
│
├── notebooks/                   # Jupyter notebooks (exploration)
│   ├── 01_data_exploration.ipynb
│   ├── 02_embedding_benchmark.ipynb
│   └── 03_retrieval_analysis.ipynb
│
├── reports/                     # Kết quả benchmark & weekly reports
│   ├── phase1/
│   ├── phase2/
│   ├── phase3/
│   ├── phase4/
│   ├── phase5/
│   ├── phase6/
│   └── weekly/                  # Weekly reports của từng người
│
├── docs/                        # Tài liệu kỹ thuật
│   ├── system/
│   │   ├── system_design_v0.md  # P1: Kiến trúc tổng thể
│   │   └── metadata_schema.md   # P3: Schema chuẩn
│   ├── api/
│   │   └── retrieval_api_contract.md  # P4: API spec
│   ├── phases/
│   │   ├── phase0_spec.md
│   │   ├── phase1_checklist.md
│   │   └── ...
│   └── team/
│       ├── roles.md             # Mô tả vai trò chi tiết
│       ├── weekly_template.md   # Template weekly report
│       └── definition_of_done.md
│
├── papers/                      # Paper drafts & references
│   ├── draft.md
│   ├── related_work.md
│   └── experiments.md
│
└── logs/                        # Runtime logs (gitignored)
    └── search_log.jsonl
```

---

## Phân công team

| Người | Vai trò | Phụ trách chính | Branch prefix |
|-------|---------|-----------------|---------------|
| **P1** | Team Lead / System / Eval | Repo, kiến trúc, API contract, benchmark, paper | `p1/` |
| **P2** | Indexing & Embedding | Keyframe extract, CLIP/SigLIP/OpenCLIP, vector DB | `p2/` |
| **P3** | Metadata & Multimodal | Caption, OCR, ASR, object detection, metadata schema | `p3/` |
| **P4** | Retrieval & Re-ranking | Hybrid search, rerank, temporal search | `p4/` |
| **P5** | Agent / UI / Workflow | Agent tools, query expansion, UI, mock contest | `p5/` |

📋 Chi tiết: [`docs/team/roles.md`](docs/team/roles.md)

---

## Roadmap 12 tuần

| Tuần | Phase | Trọng tâm | Deliverable chính |
|-----:|-------|-----------|-------------------|
| 0 | Phase 0 | Spec, repo, schema | System design + metadata schema |
| 1 | Phase 1 | Keyframe + embedding | Visual index baseline |
| 2 | Phase 1 | Search + UI | End-to-end baseline demo |
| 3 | Phase 2 | Caption/OCR/text index | Multimodal metadata |
| 4 | Phase 2 | Hybrid search | Multimodal ablation v1 |
| 5 | Phase 3 | Reranking | Better top-k ranking |
| 6 | Phase 3 | Temporal search | Multi-event query demo |
| 7 | Phase 4 | Agent tools | Tool-calling retrieval |
| 8 | Phase 4 | Query expansion | No-agent vs agent benchmark |
| 9 | Phase 5 | Competition UI | Timeline + basket + hotkeys |
| 10 | Phase 5 | Mock contest | Error analysis |
| 11 | Phase 6 | Ablation + paper | Draft sections |
| 12 | Phase 6 | Final system | Final report + paper draft |

📋 Chi tiết từng phase: [`docs/phases/`](docs/phases/)

---

## Cài đặt

> ⚠️ **TODO:** Phần này sẽ được cập nhật sau khi hoàn thiện môi trường (dự kiến cuối Phase 0).

```bash
# Clone repo
git clone https://github.com/<org>/hcmc-ai-challenge.git
cd hcmc-ai-challenge

# Tạo virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate  # Windows

# Cài dependencies
pip install -r requirements.txt

# Setup cơ bản
bash scripts/setup.sh
```

### Yêu cầu hệ thống

- Python ≥ 3.10
- GPU với CUDA ≥ 11.8 (khuyến nghị cho embedding & reranking)
- RAM ≥ 16GB
- Disk ≥ 100GB (cho dataset & embeddings)

---

## Cách sử dụng

> ⚠️ **TODO:** Phần này sẽ được cập nhật sau khi hoàn thiện từng phase.

### Chạy baseline end-to-end (Phase 1)

```bash
# Ingestion: extract keyframes + build index
bash scripts/run_baseline.sh --video-dir data/raw --subset 100

# Start UI
python src/ui/app.py
```

### Chạy evaluation

```bash
bash scripts/run_eval.sh --queries data/queries/sample_queries.jsonl
```

### Chạy ablation

```bash
bash scripts/run_ablation.sh --config configs/ablation_phase2.yaml
```

---

## Quy trình làm việc

### Branch convention

```
main                 ← stable, chỉ merge qua PR được review
develop              ← integration branch, merge từ feature branches
p1/feature-name      ← branch của P1
p2/feature-name      ← branch của P2
p3/feature-name      ← branch của P3
p4/feature-name      ← branch của P4
p5/feature-name      ← branch của P5
hotfix/issue-name    ← fix khẩn cấp trên main
```

### Quy trình PR

1. Tạo branch từ `develop`
2. Làm xong → tự test → push
3. Mở PR vào `develop` với template đã có
4. **P1 review bắt buộc** với checklist schema + API compatibility
5. Sau khi approved → merge

📋 Chi tiết: [`CONTRIBUTING.md`](CONTRIBUTING.md)

### Weekly Report

Mỗi cuối tuần, mỗi người tạo file tại `reports/weekly/week-XX-PX.md` theo template:

```markdown
## Weekly Report - Week X - Person PX

### Done
- ...

### Demo / Evidence
- Link script:
- Link result:
- Benchmark:

### Problems
- ...

### Next week
- ...
```

📋 Template đầy đủ: [`docs/team/weekly_template.md`](docs/team/weekly_template.md)

---

## Tài liệu kỹ thuật

| Tài liệu | Mô tả | Người chịu trách nhiệm |
|----------|-------|----------------------|
| [`docs/system/system_design_v0.md`](docs/system/system_design_v0.md) | Kiến trúc tổng thể | P1 |
| [`docs/system/metadata_schema.md`](docs/system/metadata_schema.md) | Schema chuẩn toàn hệ thống | P3 |
| [`docs/api/retrieval_api_contract.md`](docs/api/retrieval_api_contract.md) | API spec giữa modules | P4 |
| [`docs/team/roles.md`](docs/team/roles.md) | Chi tiết vai trò từng người | P1 |
| [`docs/team/definition_of_done.md`](docs/team/definition_of_done.md) | Tiêu chí hoàn thành task | P1 |

---

## Kết quả & Benchmark

> ⚠️ **TODO:** Bảng này sẽ được cập nhật sau từng phase.

### Ablation chính (Phase 2+)

| Method | Recall@10 | Recall@50 | Latency (ms) |
|--------|----------:|----------:|-------------:|
| CLIP only | — | — | — |
| SigLIP only | — | — | — |
| CLIP + Caption | — | — | — |
| CLIP + Caption + OCR | — | — | — |
| Hybrid full | — | — | — |

📋 Báo cáo đầy đủ: [`reports/`](reports/)

---

## Contributing

Xem [`CONTRIBUTING.md`](CONTRIBUTING.md) để biết:
- Coding convention
- Branch & PR workflow
- Definition of Done
- Commit message format

---

## License

Internal — HCMC AI Challenge 2026, AIO_DataDominator.
