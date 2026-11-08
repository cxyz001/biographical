import asyncio
import hashlib
import tempfile
import unittest
from pathlib import Path

from document_lab import MAX_BYTES, analyze, bounded_map


class AnalysisTests(unittest.TestCase):
    def test_text_report_and_repeatability(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sample.txt"
            raw = "Python python\n\n工程\n".encode("utf-8")
            path.write_bytes(raw)
            report = analyze(path)
            self.assertEqual(report.sha256, hashlib.sha256(raw).hexdigest())
            self.assertEqual(report.nonempty_lines, 2)
            self.assertEqual(report.top_terms[0], ("python", 2))
            self.assertEqual(report, analyze(path))

    def test_invalid_input(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sample.txt"
            path.write_bytes(b"\xff")
            with self.assertRaises(UnicodeError):
                analyze(path)
            path.write_bytes(b"x" * (MAX_BYTES + 1))
            with self.assertRaises(ValueError):
                analyze(path)
            with self.assertRaises(ValueError):
                analyze(path, 0)
            with self.assertRaises(FileNotFoundError):
                analyze(Path(folder) / "missing")


class AsyncTests(unittest.IsolatedAsyncioTestCase):
    async def test_bound_and_order(self):
        active = peak = 0

        async def fetch(value):
            nonlocal active, peak
            active += 1
            peak = max(active, peak)
            try:
                await asyncio.sleep(0.001)
                return value.upper()
            finally:
                active -= 1

        result = await bounded_map(["a", "b", "c"], fetch, limit=2)
        self.assertEqual(result, ["A", "B", "C"])
        self.assertLessEqual(peak, 2)
        self.assertEqual(active, 0)

    async def test_failure_cancels_sibling(self):
        started = asyncio.Event()
        cleaned = asyncio.Event()

        async def fetch(value):
            if value == "bad":
                await started.wait()
                raise RuntimeError("模拟依赖失败")
            started.set()
            try:
                await asyncio.Event().wait()
            finally:
                cleaned.set()

        with self.assertRaises(ExceptionGroup) as caught:
            await bounded_map(["slow", "bad"], fetch, limit=2)
        self.assertTrue(any(isinstance(e, RuntimeError) for e in caught.exception.exceptions))
        self.assertTrue(cleaned.is_set())

    async def test_timeout_and_validation(self):
        cleaned = asyncio.Event()

        async def fetch(value):
            try:
                await asyncio.Event().wait()
            finally:
                cleaned.set()

        with self.assertRaises(TimeoutError):
            await bounded_map(["a"], fetch, timeout=0.02)
        self.assertTrue(cleaned.is_set())
        with self.assertRaises(ValueError):
            await bounded_map(["a"], fetch, limit=0)
        with self.assertRaises(ValueError):
            await bounded_map(["a"] * 101, fetch)


if __name__ == "__main__":
    unittest.main()
