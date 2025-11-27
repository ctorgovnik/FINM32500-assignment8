import logging
import os
from pathlib import Path
from typing import Optional


def setup_logger(process_name: str, log_dir: str = "logs", level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger for a specific process with both file and console handlers.
    
    Args:
        process_name: Name of the process (e.g., 'gateway', 'strategy', 'orderbook')
        log_dir: Directory to store log files (default: 'logs')
        level: Logging level (default: INFO)
    
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(process_name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # File handler - writes to process-specific log file
    log_file = log_path / f"{process_name}.log"
    file_handler = logging.FileHandler(log_file, mode='w')
    file_handler.setLevel(level)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler - writes to stdout
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    logger.info(f"Logger initialized for {process_name}. Log file: {log_file}")
    
    return logger


def get_logger(process_name: str) -> logging.Logger:
    """
    Get an existing logger or create a new one if it doesn't exist.
    
    Args:
        process_name: Name of the process
    
    Returns:
        Logger instance
    """
    logger = logging.getLogger(process_name)
    if not logger.handlers:
        # Logger not set up yet, set it up with defaults
        return setup_logger(process_name)
    return logger

