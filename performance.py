import logging
import os
import json
import time

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
LOG_PATH = os.path.join(LOG_DIR, "performance.log")

os.makedirs(LOG_DIR, exist_ok=True)

_perf_logger = logging.getLogger("performance")
_perf_logger.setLevel(logging.INFO)

if not _perf_logger.handlers:
    fh = logging.FileHandler(LOG_PATH)
    formatter = logging.Formatter(
        "%(asctime)s %(processName)s %(levelname)s %(message)s"
    )
    fh.setFormatter(formatter)
    _perf_logger.addHandler(fh)

def log_metric(metric: str, **fields):
    record = {"metric": metric, "timestamp": time.time()}
    record.update(fields)
    _perf_logger.info(json.dumps(record))