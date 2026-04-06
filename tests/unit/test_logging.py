"""
Unit tests for logging system
"""

import pytest
import logging
from pathlib import Path
from src.logging.logger import setup_logging, get_logger


class TestLoggingSetup:
    """Tests for logging setup"""
    
    def test_get_logger(self):
        """Test getting logger"""
        logger = get_logger("test")
        assert logger is not None
        assert isinstance(logger, logging.Logger)
    
    def test_logger_name(self):
        """Test logger naming"""
        logger = get_logger("mymodule")
        assert "siliconsoul" in logger.name


class TestLoggingConfiguration:
    """Tests for logging configuration"""
    
    def test_setup_logging_console(self):
        """Test console logging setup"""
        setup_logging(log_level="INFO")
        logger = get_logger("test")
        
        # Should not raise
        logger.info("Test message")
    
    def test_setup_logging_file(self, tmp_path):
        """Test file logging setup"""
        log_file = str(tmp_path / "test.log")
        setup_logging(log_level="DEBUG", log_file=log_file)
        
        logger = get_logger("test")
        logger.info("Test message")
        
        # Log file should exist
        assert Path(log_file).exists()
    
    def test_logging_levels(self):
        """Test different logging levels"""
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            setup_logging(log_level=level)
            logger = get_logger("test")
            assert logger is not None


class TestLoggerUsage:
    """Tests for logger usage"""
    
    def test_logger_info(self):
        """Test info logging"""
        logger = get_logger("test")
        logger.info("Test info message")
    
    def test_logger_warning(self):
        """Test warning logging"""
        logger = get_logger("test")
        logger.warning("Test warning message")
    
    def test_logger_error(self):
        """Test error logging"""
        logger = get_logger("test")
        logger.error("Test error message")
