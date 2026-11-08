"""Python 3.11+：本地文本分析 CLI 与有界异步实验，无第三方依赖。"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import re
from collections import Counter
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path

MAX_BYTES = 1_000_000


@dataclass(frozen=True)
class Report:
    source: str
    sha256: str
    characters: int
    nonempty_lines: int
    top_terms: list[tuple[str, int]]


def analyze(path: Path, top_k: int = 10) -> Report:
    if not 1 <= top_k <= 100:
        raise ValueError("top_k 必须在 1～100")
    # 最多读取上限加一字节，不依赖可能在读取前后变化的文件大小。
    with path.open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("文件超过 1 MB 教学上限")
    text = raw.decode("utf-8-sig")
    # 英文词/数字串 + 单个汉字；不是中文分词器或语义模型。
    terms = re.findall(r"[a-z0-9_]+|[\u4e00-\u9fff]", text.lower())
    counts = Counter(terms)
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:top_k]
    return Report(str(path), hashlib.sha256(raw).hexdigest(), len(text),
                  sum(bool(line.strip()) for line in text.splitlines()), ranked)


async def bounded_map(
    items: Sequence[str],
    fetch: Callable[[str], Awaitable[str]],
    *,
    limit: int = 3,
    timeout: float = 2.0,
) -> list[str]:
    """有界小批量任务：保序；一项失败时取消并等待其余项。

    输入最多 100 项，因此任务数量也有显式上限；不用于无限流。
    fetch 必须响应取消，不应包含阻塞事件循环的同步调用。
    """
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 100:
        raise ValueError("limit 必须在 1～100")
    if timeout <= 0 or len(items) > 100:
        raise ValueError("超时必须为正，批量最多 100 项")
    gate = asyncio.Semaphore(limit)

    async def run(item: str) -> str:
        async with gate:
            return await fetch(item)

    async with asyncio.timeout(timeout):
        async with asyncio.TaskGroup() as group:
            tasks = [group.create_task(run(item)) for item in items]
    return [task.result() for task in tasks]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="分析一个 UTF-8 文本；不是 AI 摘要")
    parser.add_argument("input", type=Path)
    parser.add_argument("--top", type=int, default=10)
    args = parser.parse_args(argv)
    try:
        report = analyze(args.input, args.top)
    except (OSError, UnicodeError, ValueError) as exc:
        parser.exit(2, f"分析失败：{exc}\n")
    print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
