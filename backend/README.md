# Backend

Backend chứa toàn bộ logic AI của hệ thống.

Luồng xử lý:

Video Dataset
→ Ingestion
→ Metadata
→ Indexing
→ Retrieval
→ Agent
→ API
→ Frontend

---

# app/api

Tầng giao tiếp với Frontend.

## search.py

API tìm kiếm chính.

Ví dụ:

- Text Search
- Hybrid Search
- Agent Search

---

## retrieval.py

Các API liên quan retrieval engine.

Ví dụ:

- visual retrieval
- OCR retrieval
- object retrieval

---

## agent.py

Các API gọi Agent.

Ví dụ:

- query planning
- query decomposition
- tool calling

---

## evaluation.py

API benchmark và evaluation.

---

## health.py

API kiểm tra trạng thái hệ thống.

---

# app/core

Các thành phần dùng chung.

## config.py

Đọc cấu hình từ configs/.

## constants.py

Hằng số toàn hệ thống.

## logging.py

Chuẩn logging.

## exceptions.py

Custom exceptions.

---

# app/models

Schema dữ liệu.

## metadata.py

Metadata video.

## retrieval.py

Retrieval result schema.

## search.py

Search request/response.

## candidate.py

Candidate schema.

## agent.py

Agent schema.

---

# services/ingestion

Sinh metadata.

## run_caption.py

Chạy caption pipeline.

## run_ocr.py

Chạy OCR pipeline.

## run_asr.py

Chạy ASR pipeline.

## run_object_detection.py

Chạy object detection.

## caption_pipeline.py

Triển khai caption model.

## ocr_pipeline.py

Triển khai OCR model.

## asr_pipeline.py

Triển khai ASR model.

## object_pipeline.py

Triển khai object detector.

## metadata_builder.py

Gộp metadata từ các nguồn.

## schema_validator.py

Kiểm tra metadata hợp lệ.

Output:

- captions
- OCR
- ASR
- objects
- metadata

---

# services/indexing

Xây dựng hệ thống index.

## extract_keyframes.py

Tách keyframe.

## extract_segments.py

Tách segment.

## build_clip_index.py

Embedding bằng CLIP.

## build_openclip_index.py

Embedding bằng OpenCLIP.

## build_sigclip_index.py

Embedding bằng SigLIP.

## embedding_factory.py

Khởi tạo embedding model.

## vector_db.py

Làm việc với FAISS/Qdrant/Milvus.

## neighbor_index.py

Index frame lân cận.

## index_manager.py

Điều phối toàn bộ indexing.

Output:

- embeddings
- vector database
- retrieval index

---

# services/retrieval

Tầng tìm kiếm.

## search_visual.py

Visual Retrieval.

## search_caption.py

Caption Retrieval.

## search_ocr.py

OCR Retrieval.

## search_object.py

Object Retrieval.

## hybrid_search.py

Kết hợp nhiều nguồn tìm kiếm.

## rerank.py

Re-ranking.

## temporal_search.py

Temporal Retrieval.

## candidate_merger.py

Gộp candidate.

## score_fusion.py

Kết hợp score.

## retrieval_manager.py

Điều phối retrieval pipeline.

Output:

- ranked candidates

---

# services/agent

Agentic Retrieval.

## planner.py

Lập kế hoạch tìm kiếm.

## query_expansion.py

Mở rộng query.

## query_rewriter.py

Viết lại query.

## query_decomposer.py

Tách query phức tạp.

## tool_registry.py

Đăng ký tool.

## tool_executor.py

Thực thi tool.

## result_fusion.py

Gộp kết quả.

## explanation.py

Sinh giải thích.

## prompts.py

Prompt templates.

Output:

- retrieval plan
- final answer
- explanations

---

# services/evaluation

Đánh giá hệ thống.

## benchmark.py

Benchmark.

## metrics.py

Recall, MRR, Latency.

## evaluator.py

Đánh giá tổng thể.

## ablation.py

Ablation study.

## leaderboard.py

Leaderboard.

## report_generator.py

Sinh báo cáo.

Output:

- metrics
- reports
- experiment results