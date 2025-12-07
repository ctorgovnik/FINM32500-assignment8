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
    Compute average latency (ms) using pre-computed latency samples.

    Returns:
        Average latency in ms, or None if no samples are found.
    """
    if not perf_log_path.exists():
        return None

    latencies_ms: list[float] = []

    with perf_log_path.open("r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Only look at latency events
            if row.get("event") != "latency":
                continue

            duration_str = row.get("duration_ms", "")
            if not duration_str:
                continue

            try:
                lat = float(duration_str)
            except ValueError:
                continue

            latencies_ms.append(lat)

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

def calculate_throughput(perf_log_path: Path = PERF_LOG_PATH) -> float | None:
    """
    Compute throughput in ticks per second, based on Gateway price_tick_emitted events.

    Throughput = (number_of_ticks - 1) / (last_tick_ts - first_tick_ts)

    Returns:
        ticks per second as float, or None if not enough data.
    """
    if not perf_log_path.exists():
        return None

    tick_timestamps: list[float] = []

    with perf_log_path.open("r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("component") == "Gateway" and row.get("event") == "price_tick_emitted":
                try:
                    ts = float(row["timestamp"])
                except (KeyError, ValueError):
                    continue
                tick_timestamps.append(ts)

    if len(tick_timestamps) < 2:
        return None

    tick_timestamps.sort()
    first_ts = tick_timestamps[0]
    last_ts = tick_timestamps[-1]
    elapsed = last_ts - first_ts

    if elapsed <= 0:
        return None

    return (len(tick_timestamps) - 1) / elapsed

def calculate_resilience_stats(perf_log_path: Path = PERF_LOG_PATH) -> dict[str, int]:
    """
    Summarize behavior under dropped connections / missing data.

    Returns a dict with counts:
      - "client_disconnects"
      - "missing_data"
      - "stale_data"
    """
    stats = {
        "client_disconnects": 0,
        "missing_data": 0,
        "stale_data": 0,
    }

    if not perf_log_path.exists():
        return stats

    with perf_log_path.open("r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            event = row.get("event", "")
            component = row.get("component", "")

            if component == "Gateway" and event == "client_disconnected":
                stats["client_disconnects"] += 1
            elif component == "Strategy" and event == "missing_data":
                stats["missing_data"] += 1
            elif component == "Strategy" and event == "stale_data":
                stats["stale_data"] += 1

    return stats

def write_performance_report(
    perf_log_path: Path = PERF_LOG_PATH,
    output_path: Path = Path("performance.md")
) -> None:

    latency = calculate_average_latency(perf_log_path)
    shm = read_shared_memory_size(perf_log_path)
    throughput = calculate_throughput(perf_log_path)
    resilience = calculate_resilience_stats(perf_log_path)

    report = ["# Performance Report\n"]

    # ---------------- Latency ----------------
    report.append("## Latency (Tick → Trade Decision)")
    if latency is not None:
        report.append(f"- Average latency: **{latency:.2f} ms**")
    else:
        report.append("- Average latency: **N/A (no matching tick+decision events)**")
    report.append("")

    # ---------------- Throughput ----------------
    report.append("## Throughput (Ticks per Second)")
    if throughput is not None:
        report.append(f"- Average throughput: **{throughput:.2f} ticks/sec**")
    else:
        report.append("- Throughput: **N/A (not enough tick data)**")
    report.append("")

    # ---------------- Shared Memory ----------------
    report.append("## Shared Memory Footprint")
    if shm:
        report.append(f"- Shared memory size: **{shm} bytes** ({shm/1024:.2f} KB)")
    else:
        report.append("- Shared memory size: **Not Recorded**")
    report.append("")
    report.append("---")
    report.append("Generated from `performance.csv`\n")

    # ---------- Dropped Connections / Missing Data ----------
    report.append("## Behavior under Dropped Connections / Missing Data")
    report.append(
        f"- Gateway client disconnects: **{resilience['client_disconnects']}**"
    )
    report.append(
        f"- Missing data reads (price/timestamp is None): **{resilience['missing_data']}**"
    )
    report.append(
        f"- Stale data reads (timestamp did not advance): **{resilience['stale_data']}**"
    )
    report.append("")
    report.append("---")
    report.append("Generated from `performance.csv`\n")

    output_path.write_text("\n".join(report), encoding="utf-8")
    print(f"performance.md written → {output_path}")

if __name__ == "__main__":
    write_performance_report()