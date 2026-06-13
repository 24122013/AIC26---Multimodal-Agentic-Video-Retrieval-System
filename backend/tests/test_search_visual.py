from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from backend.app.services.metadata.metadata_store import MetadataStore
from backend.app.services.retrieval.search_visual import (
    VisualSearchConfig,
    VisualSearchEngine,
    normalize_query_vector,
)


class FakeEncoder:
    def encode(self, query: str) -> np.ndarray:
        if query != "a man cooking in a kitchen":
            raise AssertionError(f"unexpected query: {query}")
        return np.array([3.0, 4.0], dtype="float32")


class FakeSearcher:
    def __init__(self) -> None:
        self.seen_vector = None
        self.seen_top_k = None

    def search(self, vector: np.ndarray, top_k: int) -> tuple[np.ndarray, np.ndarray]:
        self.seen_vector = vector
        self.seen_top_k = top_k
        return (
            np.array([[0.91, 0.75, -1.0]], dtype="float32"),
            np.array([[1, 0, -1]], dtype="int64"),
        )


class VisualSearchEngineTest(unittest.TestCase):
    def test_normalize_query_vector_returns_single_unit_vector(self) -> None:
        vector = normalize_query_vector(np.array([3.0, 4.0], dtype="float32"))

        self.assertEqual(vector.shape, (1, 2))
        self.assertAlmostEqual(float(np.linalg.norm(vector)), 1.0, places=6)

    def test_search_maps_faiss_indices_to_retrieval_results(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            frame_map_path = Path(tmp_dir) / "frame_map.json"
            frame_map = {
                "0": {
                    "frame_id": "FRAME_L01_V001_000001",
                    "video_id": "L01_V001",
                    "shot_id": "SHOT_L01_V001_000001",
                    "segment_id": "SEG_L01_V001_000001",
                    "timestamp": 0.0,
                    "timestamp_source": "interval",
                    "timestamp_confidence": 0.5,
                    "keyframe_path": "data/keyframes/L01_V001/000001.jpg",
                    "thumbnail_path": "data/keyframes/L01_V001/000001.jpg",
                },
                "1": {
                    "frame_id": "FRAME_L01_V001_000002",
                    "video_id": "L01_V001",
                    "shot_id": "SHOT_L01_V001_000002",
                    "segment_id": "SEG_L01_V001_000002",
                    "timestamp": 2.0,
                    "timestamp_source": "interval",
                    "timestamp_confidence": 0.5,
                    "keyframe_path": "data/keyframes/L01_V001/000002.jpg",
                    "thumbnail_path": "data/keyframes/L01_V001/000002.jpg",
                },
            }
            frame_map_path.write_text(json.dumps(frame_map), encoding="utf-8")

            searcher = FakeSearcher()
            engine = VisualSearchEngine(
                config=VisualSearchConfig(default_top_k=3),
                encoder=FakeEncoder(),
                searcher=searcher,
                metadata_store=MetadataStore.from_frame_map(frame_map_path),
            )

            response = engine.search("a man cooking in a kitchen")

            self.assertEqual(searcher.seen_top_k, 3)
            self.assertAlmostEqual(float(np.linalg.norm(searcher.seen_vector)), 1.0, places=6)
            self.assertEqual(len(response.results), 2)
            self.assertEqual(response.results[0].faiss_index, 1)
            self.assertEqual(response.results[0].video_id, "L01_V001")
            self.assertEqual(response.results[0].timestamp, 2.0)
            self.assertEqual(response.results[0].score, 0.91)
            self.assertEqual(response.results[1].frame_id, "FRAME_L01_V001_000001")


if __name__ == "__main__":
    unittest.main()
