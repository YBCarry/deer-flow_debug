# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""
Custom logging handlers for DeerFlow.
"""

import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Union


class DateRotatingFileHandler(logging.FileHandler):
    """
    A file handler that rotates log files daily and maintains a maximum number of files.
    
    Log files are named with date suffixes (e.g., interactions_2025-01-14.log)
    """
    
    def __init__(self, filename: Union[str, Path], max_files: int = 30, encoding: str = "utf-8"):
        """
        Initialize the handler.
        
        Args:
            filename: Base filename for log files
            max_files: Maximum number of log files to keep
            encoding: File encoding
        """
        self.base_filename = Path(filename)
        self.max_files = max_files
        self.current_date = datetime.now().date()
        
        # Create the dated filename
        dated_filename = self._get_dated_filename()
        
        # Ensure directory exists
        dated_filename.parent.mkdir(parents=True, exist_ok=True)
        
        super().__init__(str(dated_filename), encoding=encoding)
        
        # Clean old files
        self._cleanup_old_files()
    
    def _get_dated_filename(self, date=None):
        """Get filename with date suffix."""
        if date is None:
            date = self.current_date
        
        date_str = date.strftime("%Y-%m-%d")
        stem = self.base_filename.stem
        suffix = self.base_filename.suffix
        
        return self.base_filename.parent / f"{stem}_{date_str}{suffix}"
    
    def emit(self, record):
        """Emit a record, rotating the file if date has changed."""
        today = datetime.now().date()
        
        if today != self.current_date:
            # Date has changed, rotate to new file
            self.close()
            self.current_date = today
            new_filename = self._get_dated_filename()
            self.baseFilename = str(new_filename)
            self.stream = None  # Force reopening
            self._cleanup_old_files()
        
        super().emit(record)
    
    def _cleanup_old_files(self):
        """Remove old log files beyond max_files limit."""
        try:
            pattern = f"{self.base_filename.stem}_*.log"
            log_files = list(self.base_filename.parent.glob(pattern))
            
            if len(log_files) <= self.max_files:
                return
            
            # Sort by modification time and remove oldest files
            log_files.sort(key=lambda x: x.stat().st_mtime)
            files_to_remove = log_files[:-self.max_files]
            
            for file_path in files_to_remove:
                try:
                    file_path.unlink()
                except OSError:
                    pass  # Ignore errors when removing files
                    
        except Exception:
            pass  # Ignore cleanup errors