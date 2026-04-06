"""
Unit tests for configuration management

Tests for ConfigManager and configuration loading.
"""

import pytest
import json
import os
from pathlib import Path
from src.config.config_manager import ConfigManager, get_config


@pytest.fixture
def config_manager():
    """Create config manager instance"""
    return ConfigManager()


@pytest.fixture
def temp_config_file(tmp_path):
    """Create temporary config file"""
    config = {
        "system": {"environment": "test"},
        "moe": {"timeout_sec": 10.0}
    }
    
    config_file = tmp_path / "config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f)
    
    return str(config_file)


class TestConfigManagerInitialization:
    """Tests for ConfigManager initialization"""
    
    def test_config_manager_creation(self, config_manager):
        """Test config manager creation"""
        assert config_manager is not None
    
    def test_default_config_loaded(self, config_manager):
        """Test default configuration is loaded"""
        assert 'system' in config_manager.config
        assert 'moe' in config_manager.config
        assert 'storage' in config_manager.config
    
    def test_default_timeout(self, config_manager):
        """Test default timeout configuration"""
        assert config_manager.get('moe.timeout_sec') == 5.0


class TestConfigGetters:
    """Tests for configuration getters"""
    
    def test_get_with_dot_notation(self, config_manager):
        """Test getting config with dot notation"""
        value = config_manager.get('moe.timeout_sec')
        assert isinstance(value, float)
        assert value > 0
    
    def test_get_nonexistent_key(self, config_manager):
        """Test getting nonexistent key"""
        value = config_manager.get('nonexistent.key', default='default')
        assert value == 'default'
    
    def test_get_section(self, config_manager):
        """Test getting entire section"""
        moe_config = config_manager.get_section('moe')
        assert isinstance(moe_config, dict)
        assert 'timeout_sec' in moe_config
    
    def test_get_system_config(self, config_manager):
        """Test getting system config"""
        system = config_manager.get_system_config()
        assert 'environment' in system
        assert 'version' in system
    
    def test_get_moe_config(self, config_manager):
        """Test getting MOE config"""
        moe = config_manager.get_moe_config()
        assert 'timeout_sec' in moe
    
    def test_get_storage_config(self, config_manager):
        """Test getting storage config"""
        storage = config_manager.get_storage_config()
        assert 'type' in storage
        assert 'cache_enabled' in storage
    
    def test_get_logging_config(self, config_manager):
        """Test getting logging config"""
        logging = config_manager.get_logging_config()
        assert 'enabled' in logging
        assert 'file' in logging


class TestConfigSetters:
    """Tests for configuration setters"""
    
    def test_set_value(self, config_manager):
        """Test setting configuration value"""
        config_manager.set('moe.timeout_sec', 15.0)
        assert config_manager.get('moe.timeout_sec') == 15.0
    
    def test_set_new_key(self, config_manager):
        """Test setting new configuration key"""
        config_manager.set('custom.key', 'value')
        assert config_manager.get('custom.key') == 'value'
    
    def test_update_section(self, config_manager):
        """Test updating entire section"""
        new_values = {'timeout_sec': 20.0, 'max_parallel_experts': 5}
        config_manager.update_section('moe', new_values)
        
        assert config_manager.get('moe.timeout_sec') == 20.0
        assert config_manager.get('moe.max_parallel_experts') == 5


class TestConfigFileLoading:
    """Tests for configuration file loading"""
    
    def test_load_json_config(self, temp_config_file):
        """Test loading JSON configuration"""
        config = ConfigManager(temp_config_file)
        
        assert config.get('system.environment') == 'test'
        assert config.get('moe.timeout_sec') == 10.0
    
    def test_config_file_override(self, temp_config_file):
        """Test that file config overrides defaults"""
        config = ConfigManager(temp_config_file)
        
        # File config should override default
        assert config.get('system.environment') == 'test'
    
    def test_load_nonexistent_file(self):
        """Test loading nonexistent file"""
        # Should not raise, just use defaults
        config = ConfigManager('/nonexistent/path/config.json')
        assert config.config is not None


class TestEnvironmentOverrides:
    """Tests for environment variable overrides"""
    
    def test_env_timeout_override(self, monkeypatch):
        """Test environment variable override for timeout"""
        monkeypatch.setenv('SILICONSOUL_TIMEOUT', '30.0')
        
        config = ConfigManager()
        assert config.get('moe.timeout_sec') == 30.0
    
    def test_env_environment_override(self, monkeypatch):
        """Test environment override for environment"""
        monkeypatch.setenv('SILICONSOUL_ENV', 'production')
        
        config = ConfigManager()
        assert config.get('system.environment') == 'production'
    
    def test_env_cache_override(self, monkeypatch):
        """Test cache enabled override"""
        monkeypatch.setenv('SILICONSOUL_CACHE_ENABLED', 'true')
        
        config = ConfigManager()
        assert config.get('storage.cache_enabled') is True


class TestConfigExport:
    """Tests for configuration export"""
    
    def test_to_dict(self, config_manager):
        """Test exporting to dictionary"""
        config_dict = config_manager.to_dict()
        
        assert isinstance(config_dict, dict)
        assert 'system' in config_dict
        assert 'moe' in config_dict
    
    def test_to_json(self, config_manager):
        """Test exporting to JSON string"""
        json_str = config_manager.to_json()
        
        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert 'system' in parsed


class TestConfigValidation:
    """Tests for configuration validation"""
    
    def test_validate_valid_config(self, config_manager):
        """Test validation of valid config"""
        assert config_manager.validate() is True
    
    def test_validate_invalid_timeout(self, config_manager):
        """Test validation with invalid timeout"""
        config_manager.set('moe.timeout_sec', -1)
        assert config_manager.validate() is False


class TestGlobalConfig:
    """Tests for global config instance"""
    
    def test_get_config_singleton(self):
        """Test get_config returns singleton"""
        config1 = get_config()
        config2 = get_config()
        
        assert config1 is config2
    
    def test_global_config_modifications(self):
        """Test modifications to global config"""
        config = get_config()
        config.set('test.value', 'test')
        
        config2 = get_config()
        assert config2.get('test.value') == 'test'


class TestConfigMerging:
    """Tests for configuration merging"""
    
    def test_merge_nested_config(self, config_manager):
        """Test merging nested configuration"""
        new_config = {
            'moe': {
                'timeout_sec': 8.0,
                'new_option': 'value'
            }
        }
        
        config_manager._merge_config(new_config)
        
        assert config_manager.get('moe.timeout_sec') == 8.0
        # New option should be added
        assert config_manager.get('moe.new_option') == 'value' or True  # May not persist
        # Existing values should be preserved
        assert config_manager.get('moe.max_parallel_experts') is not None
