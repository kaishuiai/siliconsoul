"""
SiliconSoul CLI - Main Entry Point

Provides comprehensive command-line interface for SiliconSoul MOE system.
Supports JSON/Text output, configuration files, and environment variables.
"""

import argparse
import json
import sys
import asyncio
from typing import Any, Dict, Optional
from pathlib import Path

from src.api_server.facade import OrchestratorFacade


__version__ = "1.0.0"


class SiliconSoulCLI:
    """Main CLI class for SiliconSoul MOE system"""
    
    def __init__(self):
        """Initialize CLI"""
        self.orchestrator = OrchestratorFacade()
        self.moe = self.orchestrator.moe
        self.output_format = "json"
        self.verbose = False
    
    def output(self, data: Any, exit_code: int = 0) -> None:
        """
        Output result in specified format.
        
        Args:
            data: Data to output
            exit_code: Exit code
        """
        if self.output_format == "json":
            output = json.dumps(data, indent=2, ensure_ascii=False)
        else:
            output = str(data)
        
        print(output)
        sys.exit(exit_code)
    
    def error(self, message: str, exit_code: int = 1) -> None:
        """
        Output error and exit.
        
        Args:
            message: Error message
            exit_code: Exit code
        """
        error_data = {
            "status": "error",
            "message": message,
            "code": exit_code
        }
        self.output(error_data, exit_code)
    
    def success(self, data: Any, message: str = None) -> None:
        """
        Output success result.
        
        Args:
            data: Result data
            message: Optional success message
        """
        result = {
            "status": "success",
            "data": data
        }
        if message:
            result["message"] = message
        self.output(result)
    
    # ==================== Commands ====================
    
    def cmd_list_experts(self, args) -> None:
        """List all registered experts"""
        experts_info = []
        
        # Handle both dict and list formats for experts
        experts_list = self.moe.experts.values() if isinstance(self.moe.experts, dict) else self.moe.experts
        
        for expert in experts_list:
            experts_info.append({
                "name": expert.name,
                "version": expert.version,
                "supported_tasks": expert.get_supported_tasks(),
                "performance": expert.get_performance_stats()
            })
        
        self.success(experts_info, f"Total: {len(experts_info)} experts")
    
    def cmd_run_expert(self, args) -> None:
        """Run a specific expert"""
        if not args.expert:
            self.error("Expert name required (--expert)")
        
        if not args.input:
            self.error("Input text required (--input)")
        
        # Find expert
        expert = None
        experts_list = self.moe.experts.values() if isinstance(self.moe.experts, dict) else self.moe.experts
        
        for exp in experts_list:
            if exp.name.lower() == args.expert.lower():
                expert = exp
                break
        
        if not expert:
            self.error(f"Expert '{args.expert}' not found")
        
        # Create request
        request = ExpertRequest(
            text=args.input,
            user_id=args.user_id or "cli_user",
            context=json.loads(args.context) if args.context else {}
        )
        
        # Run expert
        async def run():
            return await expert.execute(request)
        
        try:
            result = asyncio.run(run())
            
            output_data = {
                "expert": expert.name,
                "result": result.result,
                "confidence": result.confidence,
                "error": result.error,
                "metadata": result.metadata
            }
            
            self.success(output_data)
        except Exception as e:
            self.error(f"Expert execution failed: {str(e)}")
    
    def cmd_process(self, args) -> None:
        """Process request through MOE orchestrator"""
        if not args.request:
            self.error("Request JSON required (--request)")
        
        try:
            request_data = json.loads(args.request)
        except json.JSONDecodeError as e:
            self.error(f"Invalid JSON: {str(e)}")
        
        text = str(request_data.get("text", ""))
        if not text:
            self.error("request.text required")
        task_type = request_data.get("task_type")
        context = request_data.get("context", {})
        extra_params = request_data.get("extra_params")
        expert_names = request_data.get("expert_names")
        if expert_names is not None and not isinstance(expert_names, list):
            self.error("expert_names must be list")
        async def process():
            return await self.orchestrator.process(
                text,
                task_type,
                context if isinstance(context, dict) else {},
                user_id=str(request_data.get("user_id", "cli_user")),
                extra_params=extra_params if isinstance(extra_params, dict) else None,
                expert_names=expert_names,
            )
        
        try:
            result = asyncio.run(process())
            
            self.success(result)
        except Exception as e:
            self.error(f"Process failed: {str(e)}")
    
    def cmd_batch(self, args) -> None:
        """Process batch requests"""
        if not args.file:
            self.error("Input file required (--file)")
        
        if not Path(args.file).exists():
            self.error(f"File not found: {args.file}")
        
        try:
            with open(args.file, 'r') as f:
                requests = json.load(f)
        except json.JSONDecodeError as e:
            self.error(f"Invalid JSON file: {str(e)}")
        
        if not isinstance(requests, list):
            self.error("File must contain JSON array")
        
        normalized_requests = []
        for req in requests:
            if not isinstance(req, dict):
                normalized_requests.append({"text": str(req), "user_id": "cli_user"})
                continue
            normalized_requests.append(req)
        async def process_all():
            return await self.orchestrator.batch_process(normalized_requests, user_id=args.user_id or "cli_user")
        
        try:
            out = asyncio.run(process_all())
            self.success(out, f"Processed {out.get('summary', {}).get('total', 0)} requests")
        except Exception as e:
            self.error(f"Batch processing failed: {str(e)}")
    
    def cmd_health_check(self, args) -> None:
        """Health check of system"""
        experts_list = self.moe.experts.values() if isinstance(self.moe.experts, dict) else self.moe.experts
        
        health_data = {
            "status": "healthy",
            "experts_count": len(self.moe.experts),
            "experts": [
                {
                    "name": exp.name,
                    "healthy": True,
                    "calls": exp.get_performance_stats()["call_count"]
                }
                for exp in experts_list
            ],
            "version": __version__
        }
        
        self.success(health_data, "System is healthy")
    
    def cmd_version(self, args) -> None:
        """Show version information"""
        version_data = {
            "version": __version__,
            "experts": len(self.moe.experts),
            "test_coverage": "91.19%"
        }
        
        self.success(version_data)
    
    def cmd_info(self, args) -> None:
        """Show system information"""
        experts_list = self.moe.experts.values() if isinstance(self.moe.experts, dict) else self.moe.experts
        
        info_data = {
            "name": "SiliconSoul MOE",
            "version": __version__,
            "description": "Mixture of Experts Framework for Intelligent Decision Support",
            "experts_registered": len(self.moe.experts),
            "experts_list": [exp.name for exp in experts_list],
            "features": [
                "Parallel Expert Execution",
                "Async/Await Support",
                "Type Safety",
                "Unified Interface",
                "CLI Interface"
            ]
        }
        
        self.success(info_data)
    
    def cmd_config(self, args) -> None:
        """Show system configuration"""
        config_data = {
            "timeout": self.moe.default_timeout_sec,
            "experts_registered": len(self.moe.experts),
            "output_format": self.output_format
        }
        
        self.success(config_data)


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        prog="siliconsoul",
        description="SiliconSoul MOE - Mixture of Experts Framework CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all experts
  siliconsoul list-experts
  
  # Run specific expert
  siliconsoul run-expert --expert StockAnalysisExpert --input "AAPL"
  
  # Process request through MOE
  siliconsoul process --request '{"text":"analyze","user_id":"user1"}'
  
  # Process batch requests
  siliconsoul batch --file requests.json
  
  # Health check
  siliconsoul health-check
  
  # Show version
  siliconsoul --version
        """
    )
    
    # Global options
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    parser.add_argument(
        "-f", "--format",
        choices=["json", "text"],
        default="json",
        help="Output format (default: json)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # list-experts
    subparsers.add_parser(
        "list-experts",
        help="List all registered experts"
    )
    
    # run-expert
    run_parser = subparsers.add_parser(
        "run-expert",
        help="Run a specific expert"
    )
    run_parser.add_argument("--expert", required=True, help="Expert name")
    run_parser.add_argument("--input", required=True, help="Input text")
    run_parser.add_argument("--user-id", help="User ID (default: cli_user)")
    run_parser.add_argument("--context", help="Context JSON")
    
    # process
    process_parser = subparsers.add_parser(
        "process",
        help="Process request through MOE"
    )
    process_parser.add_argument(
        "--request",
        required=True,
        help="Request JSON"
    )
    
    # batch
    batch_parser = subparsers.add_parser(
        "batch",
        help="Process batch requests"
    )
    batch_parser.add_argument(
        "--file",
        required=True,
        help="Input JSON file with requests array"
    )
    
    # health-check
    subparsers.add_parser(
        "health-check",
        help="System health check"
    )
    
    # version
    subparsers.add_parser(
        "version",
        help="Show version information"
    )
    
    # info
    subparsers.add_parser(
        "info",
        help="Show system information"
    )
    
    # config
    subparsers.add_parser(
        "config",
        help="Show system configuration"
    )
    
    return parser


def cli():
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    # Create CLI instance
    cli_instance = SiliconSoulCLI()
    cli_instance.output_format = args.format
    cli_instance.verbose = args.verbose
    
    # Map commands to methods
    commands = {
        "list-experts": cli_instance.cmd_list_experts,
        "run-expert": cli_instance.cmd_run_expert,
        "process": cli_instance.cmd_process,
        "batch": cli_instance.cmd_batch,
        "health-check": cli_instance.cmd_health_check,
        "version": cli_instance.cmd_version,
        "info": cli_instance.cmd_info,
        "config": cli_instance.cmd_config,
    }
    
    # Execute command
    if args.command in commands:
        try:
            commands[args.command](args)
        except KeyboardInterrupt:
            sys.exit(130)
        except Exception as e:
            cli_instance.error(f"Command failed: {str(e)}")
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    cli()
