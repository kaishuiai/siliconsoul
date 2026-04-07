"""
Tushare Provider 单元测试

测试 Tushare 数据提供者的各个功能
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

from src.data.tushare_provider import TushareProvider


class TestTushareProviderInit:
    """Tushare 初始化测试"""
    
    def test_init_with_token(self):
        """测试使用 token 初始化"""
        provider = TushareProvider(token="test_token_123")
        assert provider.token == "test_token_123"
    
    def test_init_without_token(self):
        """测试未提供 token 的初始化"""
        provider = TushareProvider()
        # 应该尝试从环境变量获取
        assert provider._ts is None
    
    def test_cache_initialization(self):
        """测试缓存初始化"""
        provider = TushareProvider()
        assert provider._cache == {}
        assert provider._cache_expiry == {}


class TestDailyData:
    """日线数据获取测试"""
    
    @pytest.mark.asyncio
    async def test_get_daily_data_success(self):
        """测试成功获取日线数据"""
        provider = TushareProvider(token="test_token")
        
        # Mock Tushare API 响应
        mock_data = {
            'ts_code': ['600000.SH', '600000.SH'],
            'trade_date': ['20260401', '20260402'],
            'open': [10.5, 10.6],
            'high': [10.7, 10.8],
            'low': [10.4, 10.5],
            'close': [10.6, 10.7],
            'vol': [1000000, 1100000]
        }
        
        with patch('src.data.tushare_provider.TushareProvider._init_tushare') as mock_init:
            mock_init.return_value = True
            provider._ts = Mock()
            
            # 模拟 pandas DataFrame
            import pandas as pd
            df = pd.DataFrame(mock_data)
            provider._ts.daily.return_value = df
            
            result = await provider.get_daily_data('600000.SH', '20260401', '20260402')
            
            assert result is not None
            assert len(result) == 2
            assert result[0]['close'] == 10.6
            assert result[0]['volume'] == 1000000
    
    @pytest.mark.asyncio
    async def test_get_daily_data_from_cache(self):
        """测试从缓存获取日线数据"""
        provider = TushareProvider()
        
        # 预设缓存
        cache_key = "daily:600000.SH:20260401:20260402"
        cached_data = [
            {'date': '20260401', 'close': 10.5, 'volume': 1000000}
        ]
        provider._cache[cache_key] = cached_data
        provider._cache_expiry[cache_key] = datetime.now().timestamp() + 3600
        
        result = await provider.get_daily_data('600000.SH', '20260401', '20260402')
        
        assert result == cached_data
    
    @pytest.mark.asyncio
    async def test_get_daily_data_empty(self):
        """测试获取空数据"""
        provider = TushareProvider(token="test_token")
        
        with patch('src.data.tushare_provider.TushareProvider._init_tushare') as mock_init:
            mock_init.return_value = True
            provider._ts = Mock()
            provider._ts.daily.return_value = None
            
            result = await provider.get_daily_data('INVALID.SH', '20260401', '20260402')
            
            assert result is None


class TestFinancialData:
    """财务数据获取测试"""
    
    @pytest.mark.asyncio
    async def test_get_financial_data_success(self):
        """测试成功获取财务数据"""
        provider = TushareProvider(token="test_token")
        
        with patch('src.data.tushare_provider.TushareProvider._init_tushare') as mock_init:
            mock_init.return_value = True
            provider._ts = Mock()
            
            # 模拟财务数据
            import pandas as pd
            financial_df = pd.DataFrame({
                'ts_code': ['600000.SH'],
                'trade_date': ['20260402'],
                'close': [10.7],
                'pe': [15.5],
                'pb': [1.2],
                'ps': [0.8],
                'pc': [0.5],
                'dv_ratio': [0.02],
                'dv_ttm': [0.025],
                'pb_mrq': [1.25]
            })
            provider._ts.daily_basic.return_value = financial_df
            
            result = await provider.get_financial_data('600000.SH')
            
            assert result is not None
            assert result['pe'] == 15.5
            assert result['pb'] == 1.2


class TestStockInfo:
    """股票基本信息测试"""
    
    @pytest.mark.asyncio
    async def test_get_stock_info_success(self):
        """测试成功获取股票信息"""
        provider = TushareProvider(token="test_token")
        
        with patch('src.data.tushare_provider.TushareProvider._init_tushare') as mock_init:
            mock_init.return_value = True
            provider._ts = Mock()
            
            import pandas as pd
            info_df = pd.DataFrame({
                'ts_code': ['600000.SH', '600001.SH'],
                'symbol': ['600000', '600001'],
                'name': ['浦发银行', '邯郸钢铁'],
                'area': ['上海', '河北'],
                'industry': ['银行', '钢铁'],
                'exchange': ['SSE', 'SSE']
            })
            provider._ts.stock_basic.return_value = info_df
            
            result = await provider.get_stock_info()
            
            assert result is not None
            assert len(result) == 2
            assert result[0]['name'] == '浦发银行'


class TestCacheManagement:
    """缓存管理测试"""
    
    def test_cache_valid(self):
        """测试缓存有效性检查"""
        provider = TushareProvider()
        
        # 设置有效缓存
        cache_key = "test:key"
        provider._cache[cache_key] = {"data": "test"}
        provider._cache_expiry[cache_key] = datetime.now().timestamp() + 3600
        
        assert provider._is_cache_valid(cache_key)
    
    def test_cache_expired(self):
        """测试缓存过期"""
        provider = TushareProvider()
        
        # 设置过期缓存
        cache_key = "test:key"
        provider._cache[cache_key] = {"data": "test"}
        provider._cache_expiry[cache_key] = datetime.now().timestamp() - 1  # 已过期
        
        assert not provider._is_cache_valid(cache_key)
        assert cache_key not in provider._cache
    
    def test_clear_cache(self):
        """测试清空缓存"""
        provider = TushareProvider()
        
        # 添加缓存
        provider._cache["key1"] = "value1"
        provider._cache["key2"] = "value2"
        provider._cache_expiry["key1"] = 123
        
        # 清空缓存
        provider.clear_cache()
        
        assert len(provider._cache) == 0
        assert len(provider._cache_expiry) == 0
    
    def test_cache_stats(self):
        """测试缓存统计"""
        provider = TushareProvider()
        
        provider._cache["key1"] = {"data": "value1"}
        provider._cache["key2"] = {"data": "value2"}
        
        stats = provider.cache_stats
        
        assert stats["cached_items"] == 2
        assert stats["memory_usage"] > 0


class TestErrorHandling:
    """错误处理测试"""
    
    @pytest.mark.asyncio
    async def test_get_daily_data_no_token(self):
        """测试没有 token 的情况"""
        provider = TushareProvider()  # 没有 token
        
        result = await provider.get_daily_data('600000.SH', '20260401', '20260402')
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_financial_data_exception(self):
        """测试异常处理"""
        provider = TushareProvider(token="test_token")
        
        with patch('src.data.tushare_provider.TushareProvider._init_tushare') as mock_init:
            mock_init.return_value = True
            provider._ts = Mock()
            provider._ts.daily_basic.side_effect = Exception("API Error")
            
            result = await provider.get_financial_data('600000.SH')
            
            assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
