# performance_metrics.py
import csv
import os
import time
from pathlib import Path
from typing import Any, Dict, Optional
import pandas as pd

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
PERF_LOG_PATH = LOG_DIR / "performance.csv"


def _write_row(row: Dict[str, Any]) -> None:
    """
    Append a row to logs/performance.csv with consistent columns.
    """
    row["timestamp"] = time.time()

    fieldnames = [
        "timestamp",
        "component",
        "event",
        "symbol",
        "tick_id",
        "duration_ms",
        "extra",
        "memory_bytes",
    ]

    # Fill defaults so columns are always present
    row.setdefault("component", "")
    row.setdefault("event", "")
    row.setdefault("symbol", "")
    row.setdefault("tick_id", "")
    row.setdefault("duration_ms", "")
    row.setdefault("extra", "")
    row.setdefault("memory_bytes", "")

    file_exists = PERF_LOG_PATH.exists()
    with PERF_LOG_PATH.open("a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def log_performance_event(
    component: str,
    event: str,
    *,
    symbol: str = "",
    tick_id: str = "",
    duration_ms: Optional[float] = None,
    extra: Optional[str] = None,
    memory_bytes: Optional[int] = None,
) -> None:
    """
    Generic performance event logger.
    Use this from any process. Everything goes into performance.csv.
    """
    _write_row(
        {
            "component": component,
            "event": event,
            "symbol": symbol,
            "tick_id": tick_id,
            "duration_ms": duration_ms if duration_ms is not None else "",
            "extra": extra if extra is not None else "",
            "memory_bytes": memory_bytes if memory_bytes is not None else "",
        }
    )

from pathlib import Path
import csv

def calculate_average_latency(perf_log_path: Path = PERF_LOG_PATH) -> float | None:
    """
    Compute average latency (ms) between:
      - Gateway: price_tick_emitted
      - Strategy: trade_decision

    Matching rule (per symbol):
      For each trade_decision, use the most recent price_tick_emitted
      *for the same symbol* with tick_ts <= decision_ts.
    """
    if not perf_log_path.exists():
        return None

    tick_times_by_symbol: dict[str, list[float]] = {}
    decision_times_by_symbol: dict[str, list[float]] = {}

    with perf_log_path.open("r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                ts = float(row["timestamp"])
            except (KeyError, ValueError):
                continue

            component = row.get("component", "")
            event = row.get("event", "")
            symbol = row.get("symbol", "")

            if component == "Gateway" and event == "price_tick_emitted":
                tick_times_by_symbol.setdefault(symbol, []).append(ts)

            elif component == "Strategy" and event == "trade_decision":
                decision_times_by_symbol.setdefault(symbol, []).append(ts)

    for sym in tick_times_by_symbol:
        tick_times_by_symbol[sym].sort()
    for sym in decision_times_by_symbol:
        decision_times_by_symbol[sym].sort()

    latencies_ms: list[float] = []

    for symbol, decisions in decision_times_by_symbol.items():
        ticks = tick_times_by_symbol.get(symbol, [])
        if not ticks:
            continue

        i = 0
        n_ticks = len(ticks)

        for decision_ts in decisions:
            while i + 1 < n_ticks and ticks[i + 1] <= decision_ts:
                i += 1
            if ticks[i] <= decision_ts:
                latency_ms = (decision_ts - ticks[i]) * 1000.0
                latencies_ms.append(latency_ms)

    print(f"DEBUG: matched {len(latencies_ms)} tick+decision pairs")

    if not latencies_ms:
        return None

    return sum(latencies_ms) / len(latencies_ms)

def read_shared_memory_size(perf_log_path: Path = PERF_LOG_PATH) -> int | None:

    with perf_log_path.open("r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("event") == "shared_memory_size" and row.get("memory_bytes"):
                return int(row["memory_bytes"])   # returns single known value

    return None


def write_performance_report(
    perf_log_path: Path = PERF_LOG_PATH,
    output_path: Path = Path("performance.md")
) -> None:

    latency = calculate_average_latency(perf_log_path)
    shm = read_shared_memory_size(perf_log_path)

    report = ["# Performance Report\n"]

    report.append("## Latency (Tick → Trade Decision)")
    report.append(
        f"- Average latency: **{latency:.2f} ms**" if latency is not None
        else "- Average latency: **N/A (no matching tick+decision events)**"
    )
    report.append("")

    report.append("## Shared Memory Footprint")
    if shm:
        report.append(f"- Shared memory size: **{shm} bytes** ({shm/1024:.2f} KB)")
    else:
        report.append("- Shared memory size: **Not Recorded**")
    report.append("\n---\nGenerated from `performance.csv`\n")

    output_path.write_text("\n".join(report), encoding="utf-8")

    print(f"performance.md written → {output_path}")
