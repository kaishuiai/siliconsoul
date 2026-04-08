"""
Realtime Data Provider - WebSocket 实时行情数据流

功能:
- WebSocket 连接管理
- 行情推送解析
- 实时数据缓存
- 连接断线重连
- 心跳检测
"""

import asyncio
import logging
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
import json
import time

logger = logging.getLogger(__name__)


class RealtimeDataProvider:
    """WebSocket 实时行情提供者"""
    
    def __init__(self, data_source: str = "sina"):
        """
        初始化实时数据提供者
        
        Args:
            data_source: 数据源 ("sina" 新浪财经, "tencent" 腾讯, "eastmoney" 东方财富)
        """
        self.data_source = data_source
        self.logger = logging.getLogger(__name__)
        
        self._connections = {}  # symbol -> websocket connection
        self._cache = {}        # symbol -> latest quote
        self._callbacks = {}    # symbol -> list of callbacks
        self._task_manager = {}  # symbol -> asyncio task
        
        # 配置不同数据源的 URL
        self._source_config = {
            "sina": {
                "url": "wss://feedws.sina.com.cn",
                "parser": self._parse_sina_data
            },
            "tencent": {
                "url": "wss://push.qt.qq.com/api",
                "parser": self._parse_tencent_data
            },
            "eastmoney": {
                "url": "wss://push2.eastmoney.com/WebSocketApi",
                "parser": self._parse_eastmoney_data
            }
        }
        
        self.logger.info(f"RealtimeDataProvider initialized with {data_source}")
    
    async def subscribe(
        self, symbol: str, callback: Optional[Callable] = None
    ) -> bool:
        """
        订阅股票实时行情
        
        Args:
            symbol: 股票代码（如 'sh600000'）
            callback: 数据更新回调函数
        
        Returns:
            是否订阅成功
        """
        try:
            self.logger.info(f"订阅实时行情: {symbol}")
            
            # 注册回调
            if symbol not in self._callbacks:
                self._callbacks[symbol] = []
            if callback:
                self._callbacks[symbol].append(callback)
            
            # 启动数据流任务
            if symbol not in self._task_manager:
                task = asyncio.create_task(self._stream_data(symbol))
                self._task_manager[symbol] = task
                await asyncio.sleep(0)
                if task.done():
                    exc = task.exception()
                    if exc is not None:
                        await self.unsubscribe(symbol)
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"订阅失败 {symbol}: {str(e)}")
            if callback and symbol in self._callbacks and callback in self._callbacks[symbol]:
                self._callbacks[symbol].remove(callback)
            if symbol in self._callbacks and not self._callbacks[symbol]:
                del self._callbacks[symbol]
            return False
    
    async def unsubscribe(self, symbol: str) -> bool:
        """
        取消订阅
        
        Args:
            symbol: 股票代码
        
        Returns:
            是否取消成功
        """
        try:
            self.logger.info(f"取消订阅: {symbol}")
            
            # 取消任务
            if symbol in self._task_manager:
                task = self._task_manager[symbol]
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                del self._task_manager[symbol]
            
            # 清除回调和缓存
            if symbol in self._callbacks:
                del self._callbacks[symbol]
            if symbol in self._cache:
                del self._cache[symbol]
            
            return True
            
        except Exception as e:
            self.logger.error(f"取消订阅失败 {symbol}: {str(e)}")
            return False
    
    async def get_latest(self, symbol: str) -> Optional[Dict]:
        """
        获取最新行情
        
        Args:
            symbol: 股票代码
        
        Returns:
            最新行情数据
        """
        return self._cache.get(symbol)
    
    async def _stream_data(self, symbol: str) -> None:
        """
        流式获取行情数据
        
        Args:
            symbol: 股票代码
        """
        retry_count = 0
        max_retries = 5
        
        while retry_count < max_retries:
            try:
                await self._connect_and_stream(symbol)
                retry_count = 0  # 重置重试计数
                
            except asyncio.CancelledError:
                self.logger.info(f"数据流取消: {symbol}")
                break
                
            except Exception as e:
                retry_count += 1
                wait_time = min(2 ** retry_count, 60)  # 指数退避
                self.logger.warning(
                    f"连接失败 {symbol} (重试 {retry_count}): {str(e)}，"
                    f"将在 {wait_time} 秒后重新连接"
                )
                await asyncio.sleep(wait_time)
        
        self.logger.error(f"最终连接失败 {symbol}，已放弃重试")
    
    async def _connect_and_stream(self, symbol: str) -> None:
        """
        连接到数据源并流式获取数据
        
        Args:
            symbol: 股票代码
        """
        try:
            import websockets
        except ImportError:
            self.logger.warning("websockets 库未安装，使用 HTTP 轮询模式")
            await self._poll_data(symbol)
            return
        
        config = self._source_config.get(self.data_source, {})
        url = config.get("url")
        parser = config.get("parser")
        
        if not url or not parser:
            raise ValueError(f"未知数据源: {self.data_source}")
        
        async with websockets.connect(url) as websocket:
            # 发送订阅消息
            subscribe_msg = self._get_subscribe_message(symbol)
            await websocket.send(subscribe_msg)
            
            # 接收数据循环
            last_heartbeat = time.time()
            while True:
                try:
                    # 接收数据，带超时
                    msg = await asyncio.wait_for(websocket.recv(), timeout=30)
                    
                    # 解析数据
                    data = parser(msg, symbol)
                    
                    if data:
                        # 更新缓存
                        self._cache[symbol] = data
                        
                        # 触发回调
                        for callback in self._callbacks.get(symbol, []):
                            try:
                                if asyncio.iscoroutinefunction(callback):
                                    await callback(data)
                                else:
                                    callback(data)
                            except Exception as e:
                                self.logger.error(f"回调失败: {str(e)}")
                    
                    # 更新心跳
                    last_heartbeat = time.time()
                    
                except asyncio.TimeoutError:
                    self.logger.warning(f"接收超时 {symbol}，重新连接")
                    break
    
    async def _poll_data(self, symbol: str) -> None:
        """
        HTTP 轮询模式（WebSocket 不可用时的备选）
        
        Args:
            symbol: 股票代码
        """
        while True:
            try:
                # 从 Tushare 获取数据
                data = await self._fetch_http_data(symbol)
                
                if data:
                    self._cache[symbol] = data
                    
                    # 触发回调
                    for callback in self._callbacks.get(symbol, []):
                        try:
                            if asyncio.iscoroutinefunction(callback):
                                await callback(data)
                            else:
                                callback(data)
                        except Exception as e:
                            self.logger.error(f"回调失败: {str(e)}")
                
                # 轮询间隔 5 秒
                await asyncio.sleep(5)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"轮询失败: {str(e)}")
                await asyncio.sleep(10)
    
    async def _fetch_http_data(self, symbol: str) -> Optional[Dict]:
        """HTTP 方式获取数据"""
        try:
            import aiohttp
            
            # 新浪财经接口
            url = f"https://hq.sinajs.cn/?list={symbol}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        return self._parse_sina_data(text, symbol)
                        
        except Exception as e:
            self.logger.warning(f"HTTP 请求失败: {str(e)}")
        
        return None
    
    def _get_subscribe_message(self, symbol: str) -> str:
        """获取订阅消息"""
        if self.data_source == "sina":
            return json.dumps({"list": [symbol]})
        elif self.data_source == "tencent":
            return json.dumps({"req_id": 1, "type": "subscribe", "symbol": symbol})
        else:
            return ""
    
    def _parse_sina_data(self, msg: str, symbol: str) -> Optional[Dict]:
        """解析新浪财经数据"""
        try:
            # 新浪返回格式: var hq_str_sh600000="浦发银行,10.50,10.52,...";
            if "=" not in msg or ";" not in msg:
                return None
            
            data_str = msg.split("=")[1].strip().strip('"').strip(";")
            parts = data_str.split(",")
            
            if len(parts) < 5:
                return None
            
            return {
                "symbol": symbol,
                "name": parts[0],
                "price": float(parts[1]),
                "bid": float(parts[2]),
                "ask": float(parts[3]),
                "volume": int(float(parts[8])) if len(parts) > 8 else 0,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.warning(f"解析数据失败: {str(e)}")
            return None
    
    def _parse_tencent_data(self, msg: str, symbol: str) -> Optional[Dict]:
        """解析腾讯数据"""
        # 实现腾讯数据解析
        try:
            data = json.loads(msg)
            return {
                "symbol": symbol,
                "price": data.get("price"),
                "volume": data.get("volume"),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.warning(f"解析腾讯数据失败: {str(e)}")
            return None
    
    def _parse_eastmoney_data(self, msg: str, symbol: str) -> Optional[Dict]:
        """解析东方财富数据"""
        # 实现东方财富数据解析
        try:
            data = json.loads(msg)
            return {
                "symbol": symbol,
                "price": data.get("price"),
                "volume": data.get("volume"),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.warning(f"解析东方财富数据失败: {str(e)}")
            return None
    
    async def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "subscribed_symbols": len(self._task_manager),
            "cached_quotes": len(self._cache),
            "data_source": self.data_source
        }
    
    async def cleanup(self) -> None:
        """清理资源"""
        self.logger.info("清理 WebSocket 资源")
        
        # 取消所有任务
        tasks = list(self._task_manager.values())
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        self._task_manager.clear()
        self._callbacks.clear()
        self._cache.clear()
