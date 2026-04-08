"""
Configuration Manager

Loads and manages system configuration from multiple sources:
- YAML files
- JSON files
- Environment variables
- Default values
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigManager:
    """
    Centralized configuration management.
    
    Loads configuration from multiple sources with the following priority:
    1. Environment variables
    2. YAML/JSON config files
    3. Default values
    """
    
    # Default configuration
    DEFAULT_CONFIG = {
        "system": {
            "version": "1.1.0",
            "environment": "development",
            "log_level": "INFO"
        },
        "moe": {
            "timeout_sec": 5.0,
            "max_parallel_experts": 9,
            "default_output_format": "json"
        },
        "storage": {
            "type": "memory",  # memory, file, database
            "cache_enabled": False,
            "cache_ttl_sec": 3600
        },
        "logging": {
            "enabled": True,
            "file": "logs/siliconsoul.log",
            "max_size_mb": 100,
            "backup_count": 5
        },
        "features": {
            "cli_enabled": True,
            "batch_processing": True,
            "health_check": True,
            "performance_tracking": True
        },
        "cfo": {
            "max_snippets": 5,
            "max_chars_per_snippet": 280,
            "tool_timeout_sec": 20.0,
            "enable_consulting_agent": True,
            "enable_llm": False
        }
    }
    
    def __init__(self, config_path: Optional[str] = None, **overrides: Any):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Optional path to config file (YAML or JSON)
        """
        self.config = self.DEFAULT_CONFIG.copy()
        self.config_path = config_path
        
        if config_path and os.path.exists(config_path):
            self._load_config_file(config_path)
        
        self._load_env_overrides()
        self._apply_overrides(overrides)

    def _apply_overrides(self, overrides: Dict[str, Any]) -> None:
        for key, value in overrides.items():
            if key == "storage_type":
                self.set("storage.type", value)
                continue
            if key == "timeout_sec":
                self.set("moe.timeout_sec", value)
                continue
            if "." in key:
                self.set(key, value)
                continue
            self.config[key] = value
    
    def _load_config_file(self, path: str) -> None:
        """
        Load configuration from YAML or JSON file.
        
        Args:
            path: Path to config file
        """
        try:
            if path.endswith('.yaml') or path.endswith('.yml'):
                self._load_yaml(path)
            elif path.endswith('.json'):
                self._load_json(path)
            else:
                raise ValueError(f"Unsupported config format: {path}")
        except Exception as e:
            print(f"Warning: Failed to load config file {path}: {str(e)}")
    
    def _load_yaml(self, path: str) -> None:
        """Load YAML configuration file"""
        try:
            import yaml
            with open(path, 'r') as f:
                file_config = yaml.safe_load(f)
                if file_config:
                    self._merge_config(file_config)
        except ImportError:
            print("Warning: PyYAML not installed, skipping YAML config")
        except Exception as e:
            print(f"Warning: Failed to parse YAML config: {str(e)}")
    
    def _load_json(self, path: str) -> None:
        """Load JSON configuration file"""
        try:
            with open(path, 'r') as f:
                file_config = json.load(f)
                self._merge_config(file_config)
        except Exception as e:
            print(f"Warning: Failed to parse JSON config: {str(e)}")
    
    def _load_env_overrides(self) -> None:
        """Load configuration overrides from environment variables"""
        # System settings
        if env_val := os.getenv('SILICONSOUL_ENV'):
            self.config['system']['environment'] = env_val
        
        if env_val := os.getenv('SILICONSOUL_LOG_LEVEL'):
            self.config['system']['log_level'] = env_val
        
        # MOE settings
        if env_val := os.getenv('SILICONSOUL_TIMEOUT'):
            try:
                self.config['moe']['timeout_sec'] = float(env_val)
            except ValueError:
                pass
        
        if env_val := os.getenv('SILICONSOUL_OUTPUT_FORMAT'):
            self.config['moe']['default_output_format'] = env_val
        
        # Storage settings
        if env_val := os.getenv('SILICONSOUL_STORAGE_TYPE'):
            self.config['storage']['type'] = env_val

        if env_val := os.getenv('SILICONSOUL_STORAGE_PATH'):
            self.config['storage']['connection_string'] = env_val
        
        if env_val := os.getenv('SILICONSOUL_CACHE_ENABLED'):
            self.config['storage']['cache_enabled'] = env_val.lower() in ['true', '1', 'yes']

        if env_val := os.getenv('SILICONSOUL_AUTH_ENABLED'):
            self.config.setdefault('auth', {}).setdefault('enabled', False)
            self.config['auth']['enabled'] = env_val.lower() in ['true', '1', 'yes']

        if env_val := os.getenv('SILICONSOUL_API_TOKENS'):
            tokens: Dict[str, str] = {}
            for pair in env_val.split(','):
                pair = pair.strip()
                if not pair:
                    continue
                if ':' not in pair:
                    continue
                token, user_id = pair.split(':', 1)
                token = token.strip()
                user_id = user_id.strip()
                if token and user_id:
                    tokens[token] = user_id
            self.config.setdefault('auth', {})
            self.config['auth']['tokens'] = tokens
    
    def _merge_config(self, new_config: Dict[str, Any]) -> None:
        """
        Recursively merge new configuration with existing.
        
        Args:
            new_config: Configuration dict to merge
        """
        for key, value in new_config.items():
            if key in self.config and isinstance(self.config[key], dict):
                if isinstance(value, dict):
                    self._merge_dict(self.config[key], value)
                else:
                    self.config[key] = value
            else:
                self.config[key] = value
    
    def _merge_dict(self, target: Dict, source: Dict) -> None:
        """Merge source dict into target dict"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._merge_dict(target[key], value)
            else:
                target[key] = value
    
    # ==================== Getters ====================
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation path.
        
        Args:
            key: Configuration key (e.g., 'moe.timeout_sec')
            default: Default value if key not found
        
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get entire configuration section.
        
        Args:
            section: Section name
        
        Returns:
            Section dictionary
        """
        return self.config.get(section, {})
    
    def get_system_config(self) -> Dict[str, Any]:
        """Get system configuration"""
        return self.get_section('system')
    
    def get_moe_config(self) -> Dict[str, Any]:
        """Get MOE configuration"""
        return self.get_section('moe')
    
    def get_storage_config(self) -> Dict[str, Any]:
        """Get storage configuration"""
        return self.get_section('storage')
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return self.get_section('logging')
    
    # ==================== Setters ====================
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value by dot-notation path.
        
        Args:
            key: Configuration key (e.g., 'moe.timeout_sec')
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def update_section(self, section: str, values: Dict[str, Any]) -> None:
        """
        Update entire configuration section.
        
        Args:
            section: Section name
            values: New values dictionary
        """
        if section not in self.config:
            self.config[section] = {}
        
        self._merge_dict(self.config[section], values)
    
    # ==================== Utilities ====================
    
    def to_dict(self) -> Dict[str, Any]:
        """Export configuration as dictionary"""
        return self.config.copy()

    def get_all(self) -> Dict[str, Any]:
        return self.to_dict()
    
    def to_json(self) -> str:
        """Export configuration as JSON string"""
        return json.dumps(self.config, indent=2)
    
    def save_to_file(self, path: str) -> None:
        """
        Save configuration to file.
        
        Args:
            path: Output file path (YAML or JSON)
        """
        try:
            if path.endswith('.yaml') or path.endswith('.yml'):
                import yaml
                with open(path, 'w') as f:
                    yaml.dump(self.config, f, default_flow_style=False)
            elif path.endswith('.json'):
                with open(path, 'w') as f:
                    json.dump(self.config, f, indent=2)
            else:
                raise ValueError(f"Unsupported file format: {path}")
            
            print(f"Configuration saved to {path}")
        except Exception as e:
            print(f"Error saving configuration: {str(e)}")
    
    def validate(self) -> bool:
        """
        Validate configuration.
        
        Returns:
            True if configuration is valid
        """
        # Validate required fields
        required_fields = ['system', 'moe', 'storage']
        for field in required_fields:
            if field not in self.config:
                print(f"Error: Missing required config section '{field}'")
                return False
        
        # Validate timeout value
        timeout = self.config['moe'].get('timeout_sec')
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            print("Error: moe.timeout_sec must be positive number")
            return False
        
        return True


# Global config instance
_config_instance = None


def get_config(config_path: Optional[str] = None) -> ConfigManager:
    """
    Get global configuration instance (singleton).
    
    Args:
        config_path: Optional path to config file
    
    Returns:
        ConfigManager instance
    """
    global _config_instance
    
    if _config_instance is None:
        _config_instance = ConfigManager(config_path)
    
    return _config_instance
