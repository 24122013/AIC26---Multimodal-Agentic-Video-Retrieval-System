# AIChallenge26 Multimodal Agentic Video Retrieval System

## Mục tiêu

Repo này được tổ chức để xây dựng đề tài Multimedia Retrieval với định hướng:

- Xây dựng baseline end-to-end thật sớm.
- Tách biệt Frontend và Backend để tránh chồng chéo công việc.
- Dễ mở rộng sang OCR, Caption, ASR, Object Detection, Hybrid Retrieval, Temporal Search và Agentic Retrieval.
- Dễ benchmark, ablation và viết paper.

---

## Kiến trúc tổng thể

Data
→ Ingestion
→ Indexing
→ Retrieval
→ Agent Layer
→ API
→ Frontend UI

---

## Backend

Backend là nơi xử lý toàn bộ pipeline AI:

- Ingestion dữ liệu video
- Keyframe/segment extraction
- Caption/OCR/ASR
- Embedding và Vector Database
- Hybrid Retrieval
- Re-ranking
- Temporal Search
- Agent Tool Calling
- Evaluation & Benchmark

Mọi logic AI chỉ nằm trong backend.

---

## Frontend

Frontend chỉ tập trung vào:

- Search UI
- Timeline
- Result Grid
- Candidate Basket
- Query History
- Agent Chat Interface
- Competition Workflow

Frontend giao tiếp với backend thông qua API.

---

## Luồng phát triển đề xuất

Phase 1:
- Baseline Retrieval

Phase 2:
- Multimodal Indexing

Phase 3:
- Re-ranking & Temporal Search

Phase 4:
- Agentic Retrieval

Phase 5:
- Competition UI

Phase 6:
- Ablation & Paper

---

## Nguyên tắc

- Backend và Frontend phát triển độc lập.
- Chỉ merge khi API contract ổn định.
- Mọi module mới phải benchmark được.
- Ưu tiên hệ thống chạy được trước khi tối ưu.

