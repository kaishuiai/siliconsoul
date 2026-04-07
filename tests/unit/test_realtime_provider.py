"""
Realtime Data Provider 单元测试

测试 WebSocket 实时行情提供者
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from src.data.realtime_provider import RealtimeDataProvider


class TestRealtimeProviderInit:
    """初始化测试"""
    
    def test_init_with_default_source(self):
        """测试默认数据源初始化"""
        provider = RealtimeDataProvider()
        assert provider.data_source == "sina"
    
    def test_init_with_custom_source(self):
        """测试自定义数据源初始化"""
        for source in ["sina", "tencent", "eastmoney"]:
            provider = RealtimeDataProvider(data_source=source)
            assert provider.data_source == source
    
    def test_internal_structures_initialized(self):
        """测试内部数据结构初始化"""
        provider = RealtimeDataProvider()
        assert provider._connections == {}
        assert provider._cache == {}
        assert provider._callbacks == {}
        assert provider._task_manager == {}


class TestSubscription:
    """订阅管理测试"""
    
    @pytest.mark.asyncio
    async def test_subscribe_success(self):
        """测试成功订阅"""
        provider = RealtimeDataProvider()
        
        # Mock _stream_data 避免实际连接
        with patch.object(provider, '_stream_data', new_callable=AsyncMock):
            result = await provider.subscribe('sh600000')
        
        assert result is True
        assert 'sh600000' in provider._callbacks
    
    @pytest.mark.asyncio
    async def test_subscribe_with_callback(self):
        """测试带回调的订阅"""
        provider = RealtimeDataProvider()
        callback = Mock()
        
        with patch.object(provider, '_stream_data', new_callable=AsyncMock):
            await provider.subscribe('sh600000', callback)
        
        assert callback in provider._callbacks['sh600000']
    
    @pytest.mark.asyncio
    async def test_unsubscribe_success(self):
        """测试取消订阅"""
        provider = RealtimeDataProvider()
        
        # 先订阅
        with patch.object(provider, '_stream_data', new_callable=AsyncMock) as mock_stream:
            await provider.subscribe('sh600000')
            
            # 创建模拟任务
            task = asyncio.create_task(asyncio.sleep(100))
            provider._task_manager['sh600000'] = task
        
        # 取消订阅
        result = await provider.unsubscribe('sh600000')
        
        assert result is True
        assert 'sh600000' not in provider._callbacks
        assert task.cancelled()


class TestDataCache:
    """数据缓存测试"""
    
    @pytest.mark.asyncio
    async def test_get_latest_cached(self):
        """测试获取缓存数据"""
        provider = RealtimeDataProvider()
        
        # 设置缓存数据
        cached_data = {
            'symbol': 'sh600000',
            'price': 10.5,
            'timestamp': datetime.now().isoformat()
        }
        provider._cache['sh600000'] = cached_data
        
        result = await provider.get_latest('sh600000')
        
        assert result == cached_data
    
    @pytest.mark.asyncio
    async def test_get_latest_not_cached(self):
        """测试获取不存在的数据"""
        provider = RealtimeDataProvider()
        
        result = await provider.get_latest('sh600000')
        
        assert result is None


class TestDataParsing:
    """数据解析测试"""
    
    def test_parse_sina_data_valid(self):
        """测试解析有效的新浪数据"""
        provider = RealtimeDataProvider(data_source="sina")
        
        sina_msg = 'var hq_str_sh600000="浦发银行,10.50,10.52,10.48,10.49,0,0,1000000,10500000,0,0,0,0,0,0,0,0,0,0,0,0,";'
        
        result = provider._parse_sina_data(sina_msg, 'sh600000')
        
        assert result is not None
        assert result['symbol'] == 'sh600000'
        assert result['name'] == '浦发银行'
        assert result['price'] == 10.5
        assert result['bid'] == 10.52
        assert result['ask'] == 10.48
    
    def test_parse_sina_data_invalid(self):
        """测试解析无效的新浪数据"""
        provider = RealtimeDataProvider(data_source="sina")
        
        result = provider._parse_sina_data('invalid data', 'sh600000')
        
        assert result is None
    
    def test_parse_tencent_data_valid(self):
        """测试解析腾讯数据"""
        provider = RealtimeDataProvider(data_source="tencent")
        
        msg = '{"price": 10.5, "volume": 1000000}'
        result = provider._parse_tencent_data(msg, 'sh600000')
        
        assert result is not None
        assert result['price'] == 10.5
        assert result['volume'] == 1000000


class TestSubscribeMessage:
    """订阅消息生成测试"""
    
    def test_sina_subscribe_message(self):
        """测试新浪订阅消息"""
        provider = RealtimeDataProvider(data_source="sina")
        msg = provider._get_subscribe_message('sh600000')
        
        assert 'sh600000' in msg
    
    def test_tencent_subscribe_message(self):
        """测试腾讯订阅消息"""
        provider = RealtimeDataProvider(data_source="tencent")
        msg = provider._get_subscribe_message('sh600000')
        
        assert 'sh600000' in msg
        assert 'subscribe' in msg


class TestStats:
    """统计测试"""
    
    @pytest.mark.asyncio
    async def test_get_stats(self):
        """测试获取统计信息"""
        provider = RealtimeDataProvider()
        
        # 添加一些数据
        provider._cache['sh600000'] = {'price': 10.5}
        provider._task_manager['sh600000'] = AsyncMock()
        
        stats = await provider.get_stats()
        
        assert stats['subscribed_symbols'] == 1
        assert stats['cached_quotes'] == 1
        assert stats['data_source'] == 'sina'


class TestCleanup:
    """清理测试"""
    
    @pytest.mark.asyncio
    async def test_cleanup(self):
        """测试清理资源"""
        provider = RealtimeDataProvider()
        
        # 添加模拟任务
        task1 = asyncio.create_task(asyncio.sleep(100))
        task2 = asyncio.create_task(asyncio.sleep(100))
        
        provider._task_manager['sh600000'] = task1
        provider._task_manager['sh600001'] = task2
        provider._cache['sh600000'] = {'price': 10.5}
        provider._callbacks['sh600000'] = [lambda x: None]
        
        # 清理
        await provider.cleanup()
        
        assert len(provider._task_manager) == 0
        assert len(provider._cache) == 0
        assert len(provider._callbacks) == 0
        assert task1.cancelled()
        assert task2.cancelled()


class TestErrorHandling:
    """错误处理测试"""
    
    @pytest.mark.asyncio
    async def test_subscribe_exception_handling(self):
        """测试订阅异常处理"""
        provider = RealtimeDataProvider()
        
        with patch.object(provider, '_stream_data', side_effect=Exception("Connection error")):
            result = await provider.subscribe('sh600000')
        
        # 应该返回 False 但不会抛出异常
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
