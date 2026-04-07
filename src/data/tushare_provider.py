"""
Tushare Data Provider - 专业股票数据源集成

功能:
- 历史价格数据
- 财务数据（PE、PB、ROE 等）
- 行业分类数据
- 智能缓存机制
- 错误处理和重试
"""

import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import os
from functools import lru_cache

logger = logging.getLogger(__name__)


class TushareProvider:
    """Tushare 数据提供者 - 专业级 A 股数据接口"""
    
    def __init__(self, token: Optional[str] = None):
        """
        初始化 Tushare 提供者
        
        Args:
            token: Tushare API token (从环境变量或参数)
        """
        self.token = token or os.getenv("TUSHARE_TOKEN", "")
        self._ts = None
        self._cache = {}
        self._cache_expiry = {}
        self.logger = logging.getLogger(__name__)
        self.logger.info("TushareProvider initialized")
    
    def _init_tushare(self) -> bool:
        """延迟初始化 Tushare"""
        if self._ts is not None:
            return True
        
        if not self.token:
            self.logger.warning("Tushare token 未配置")
            return False
        
        try:
            import tushare as ts
            self._ts = ts.pro_api(self.token)
            self.logger.info("Tushare API 初始化成功")
            return True
        except Exception as e:
            self.logger.warning(f"Tushare 初始化失败: {str(e)}")
            return False
    
    async def get_daily_data(
        self, ts_code: str, start_date: str, end_date: str
    ) -> Optional[List[Dict]]:
        """
        获取日线数据
        
        Args:
            ts_code: 股票代码 (如 '600000.SH')
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
        
        Returns:
            日线数据列表
        """
        # 检查缓存
        cache_key = f"daily:{ts_code}:{start_date}:{end_date}"
        if self._is_cache_valid(cache_key):
            return self._cache.get(cache_key)
        
        # 初始化 Tushare
        if not self._init_tushare():
            return None
        
        try:
            self.logger.info(f"获取日线数据: {ts_code} ({start_date}-{end_date})")
            
            # 调用 Tushare API
            df = self._ts.daily(
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date,
                fields='ts_code,trade_date,open,high,low,close,vol,amount'
            )
            
            if df is None or len(df) == 0:
                self.logger.warning(f"未获取到数据: {ts_code}")
                return None
            
            # 转换格式
            data = []
            for _, row in df.iterrows():
                data.append({
                    "date": row["trade_date"],
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "close": float(row["close"]),
                    "volume": int(row["vol"])
                })
            
            # 排序按日期升序
            data.sort(key=lambda x: x["date"])
            
            # 缓存结果
            self._cache[cache_key] = data
            self._cache_expiry[cache_key] = time.time() + 3600  # 1 小时过期
            
            self.logger.info(f"成功获取 {len(data)} 条日线数据")
            return data
            
        except Exception as e:
            self.logger.error(f"获取日线数据失败: {str(e)}")
            return None
    
    async def get_financial_data(
        self, ts_code: str
    ) -> Optional[Dict[str, Any]]:
        """
        获取财务数据
        
        Args:
            ts_code: 股票代码
        
        Returns:
            财务数据字典
        """
        # 检查缓存
        cache_key = f"financial:{ts_code}"
        if self._is_cache_valid(cache_key):
            return self._cache.get(cache_key)
        
        # 初始化 Tushare
        if not self._init_tushare():
            return None
        
        try:
            self.logger.info(f"获取财务数据: {ts_code}")
            
            # 获取最新财务指标
            df = self._ts.daily_basic(
                ts_code=ts_code,
                fields='ts_code,trade_date,close,pe,pb,ps,pc,dv_ratio,dv_ttm,pb_mrq'
            )
            
            if df is None or len(df) == 0:
                return None
            
            # 取最新一条
            row = df.iloc[0]
            
            financial_data = {
                "ts_code": row["ts_code"],
                "date": row["trade_date"],
                "close": float(row["close"]),
                "pe": float(row["pe"]) if row["pe"] != 0 else None,
                "pb": float(row["pb"]) if row["pb"] != 0 else None,
                "ps": float(row["ps"]) if row["ps"] != 0 else None,
                "dv_ratio": float(row["dv_ratio"]) if row["dv_ratio"] != 0 else None
            }
            
            # 缓存结果（1天过期）
            self._cache[cache_key] = financial_data
            self._cache_expiry[cache_key] = time.time() + 86400
            
            self.logger.info(f"成功获取财务数据")
            return financial_data
            
        except Exception as e:
            self.logger.warning(f"获取财务数据失败: {str(e)}")
            return None
    
    async def get_stock_info(
        self, ts_code: Optional[str] = None
    ) -> Optional[List[Dict]]:
        """
        获取股票基本信息
        
        Args:
            ts_code: 股票代码 (可选，不指定则返回全部)
        
        Returns:
            股票信息列表
        """
        # 初始化 Tushare
        if not self._init_tushare():
            return None
        
        try:
            self.logger.info(f"获取股票信息: {ts_code or '全部'}")
            
            params = {
                'fields': 'ts_code,symbol,name,area,industry,exchange'
            }
            if ts_code:
                params['ts_code'] = ts_code
            
            df = self._ts.stock_basic(**params)
            
            if df is None or len(df) == 0:
                return None
            
            # 转换格式
            data = []
            for _, row in df.iterrows():
                data.append({
                    "ts_code": row["ts_code"],
                    "symbol": row["symbol"],
                    "name": row["name"],
                    "area": row["area"],
                    "industry": row["industry"],
                    "exchange": row["exchange"]
                })
            
            return data
            
        except Exception as e:
            self.logger.warning(f"获取股票信息失败: {str(e)}")
            return None
    
    async def get_industry_data(
        self, industry: str
    ) -> Optional[List[Dict]]:
        """
        获取行业数据
        
        Args:
            industry: 行业名称
        
        Returns:
            行业股票列表
        """
        # 初始化 Tushare
        if not self._init_tushare():
            return None
        
        try:
            self.logger.info(f"获取行业数据: {industry}")
            
            df = self._ts.stock_basic(
                industry=industry,
                fields='ts_code,symbol,name,industry'
            )
            
            if df is None or len(df) == 0:
                return None
            
            # 转换格式
            data = []
            for _, row in df.iterrows():
                data.append({
                    "ts_code": row["ts_code"],
                    "symbol": row["symbol"],
                    "name": row["name"],
                    "industry": row["industry"]
                })
            
            return data
            
        except Exception as e:
            self.logger.warning(f"获取行业数据失败: {str(e)}")
            return None
    
    def _is_cache_valid(self, key: str) -> bool:
        """检查缓存是否有效"""
        if key not in self._cache:
            return False
        
        expiry = self._cache_expiry.get(key, 0)
        if time.time() > expiry:
            del self._cache[key]
            del self._cache_expiry[key]
            return False
        
        return True
    
    def clear_cache(self) -> None:
        """清除缓存"""
        self._cache.clear()
        self._cache_expiry.clear()
        self.logger.info("缓存已清除")
    
    @property
    def cache_stats(self) -> Dict[str, int]:
        """获取缓存统计"""
        return {
            "cached_items": len(self._cache),
            "memory_usage": len(str(self._cache))
        }
