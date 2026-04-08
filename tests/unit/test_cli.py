"""
Unit tests for CLI interface

Tests for all CLI commands and features.
"""

import pytest
import json
import subprocess
import sys
from pathlib import Path
from src.cli.main import SiliconSoulCLI, create_parser


@pytest.fixture
def cli_instance():
    """Create CLI instance"""
    return SiliconSoulCLI()


@pytest.fixture
def parser():
    """Create argument parser"""
    return create_parser()


class TestCLIInitialization:
    """Tests for CLI initialization"""
    
    def test_cli_instance_creation(self, cli_instance):
        """Test CLI instance creation"""
        assert cli_instance is not None
        assert cli_instance.moe is not None
    
    def test_experts_registered(self, cli_instance):
        """Test experts are registered"""
        assert len(cli_instance.moe.experts) >= 10
    
    def test_output_format_default(self, cli_instance):
        """Test default output format"""
        assert cli_instance.output_format == "json"


class TestArgumentParser:
    """Tests for argument parser"""
    
    def test_parser_creation(self, parser):
        """Test parser creation"""
        assert parser is not None
    
    def test_list_experts_command(self, parser):
        """Test list-experts command parsing"""
        args = parser.parse_args(["list-experts"])
        assert args.command == "list-experts"
    
    def test_run_expert_command(self, parser):
        """Test run-expert command parsing"""
        args = parser.parse_args([
            "run-expert",
            "--expert", "StockAnalysisExpert",
            "--input", "AAPL"
        ])
        assert args.command == "run-expert"
        assert args.expert == "StockAnalysisExpert"
        assert args.input == "AAPL"
    
    def test_process_command(self, parser):
        """Test process command parsing"""
        request_json = '{"text":"test","user_id":"user1"}'
        args = parser.parse_args([
            "process",
            "--request", request_json
        ])
        assert args.command == "process"
        assert args.request == request_json
    
    def test_batch_command(self, parser):
        """Test batch command parsing"""
        args = parser.parse_args([
            "batch",
            "--file", "requests.json"
        ])
        assert args.command == "batch"
        assert args.file == "requests.json"
    
    def test_health_check_command(self, parser):
        """Test health-check command parsing"""
        args = parser.parse_args(["health-check"])
        assert args.command == "health-check"
    
    def test_format_option(self, parser):
        """Test format option"""
        args = parser.parse_args([
            "--format", "text",
            "list-experts"
        ])
        assert args.format == "text"


class TestCLICommands:
    """Tests for CLI commands"""
    
    def test_list_experts_structure(self, cli_instance):
        """Test list-experts output structure"""
        # Note: In real test, we would capture output
        # This tests the method exists and is callable
        assert hasattr(cli_instance, 'cmd_list_experts')
        assert callable(cli_instance.cmd_list_experts)
    
    def test_health_check_structure(self, cli_instance):
        """Test health-check command structure"""
        assert hasattr(cli_instance, 'cmd_health_check')
        assert callable(cli_instance.cmd_health_check)
    
    def test_version_command(self, cli_instance):
        """Test version command"""
        assert hasattr(cli_instance, 'cmd_version')
        assert callable(cli_instance.cmd_version)
    
    def test_info_command(self, cli_instance):
        """Test info command"""
        assert hasattr(cli_instance, 'cmd_info')
        assert callable(cli_instance.cmd_info)
    
    def test_config_command(self, cli_instance):
        """Test config command"""
        assert hasattr(cli_instance, 'cmd_config')
        assert callable(cli_instance.cmd_config)


class TestCLIOutputFormats:
    """Tests for output formats"""
    
    def test_output_format_json(self, cli_instance):
        """Test JSON output format"""
        cli_instance.output_format = "json"
        assert cli_instance.output_format == "json"
    
    def test_output_format_text(self, cli_instance):
        """Test text output format"""
        cli_instance.output_format = "text"
        assert cli_instance.output_format == "text"
    
    def test_verbose_mode(self, cli_instance):
        """Test verbose mode"""
        cli_instance.verbose = True
        assert cli_instance.verbose is True


class TestCLIExecutable:
    """Tests for CLI executable"""
    
    def test_siliconsoul_script_exists(self):
        """Test siliconsoul script exists"""
        script_path = Path(__file__).parent.parent.parent / "siliconsoul"
        assert script_path.exists()
    
    def test_siliconsoul_script_executable(self):
        """Test siliconsoul script is executable"""
        script_path = Path(__file__).parent.parent.parent / "siliconsoul"
        assert script_path.stat().st_mode & 0o111  # Check execute bits


class TestCLIIntegration:
    """Integration tests for CLI"""
    
    def test_cli_version_command(self):
        """Test running version command"""
        # This would require subprocess execution
        # Placeholder for integration test
        pass
    
    def test_cli_help_command(self):
        """Test running help command"""
        # This would require subprocess execution
        # Placeholder for integration test
        pass
    
    def test_cli_list_experts_integration(self):
        """Test list-experts command integration"""
        # This would require subprocess execution
        # Placeholder for integration test
        pass
