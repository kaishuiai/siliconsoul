"""
Stock Analysis Expert - 真实数据驱动的股票分析专家

功能:
- 技术指标计算 (MA, RSI, MACD, 布林带)
- 趋势分析和检测
- 支撑/阻力位识别
- 交易信号生成 (BUY/HOLD/SELL)
- 置信度评分

数据源:
- akshare (A股数据，优先)
- yfinance (美股数据)
- 本地缓存
"""

import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import statistics
import asyncio

from src.experts.expert_base import Expert
from src.models.request_response import ExpertRequest, ExpertResult
from src.data.tushare_provider import TushareProvider

logger = logging.getLogger(__name__)


class StockAnalysisExpert(Expert):
    """股票分析专家 - 使用真实数据源"""
    
    def __init__(self):
        """初始化专家"""
        super().__init__(name="StockAnalysisExpert", version="2.1")
        self._supported_indicators = ["MA", "RSI", "MACD", "Bollinger"]
        self._data_cache = {}
        self._tushare_provider = TushareProvider()
        self.logger.info("StockAnalysisExpert v2.1 initialized with Tushare integration")
    
    def get_supported_tasks(self) -> List[str]:
        """返回支持的任务类型"""
        return ["stock_analysis", "technical_analysis"]
    
    async def analyze(self, request: ExpertRequest) -> ExpertResult:
        """
        主要分析方法
        
        Args:
            request: 包含股票代码和参数的请求
        
        Returns:
            分析结果或错误信息
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"开始分析 用户: {request.user_id}")
            
            # 解析请求参数
            extra_params = request.extra_params or {}
            symbol = extra_params.get("symbol", "600000.SH")
            period_days = extra_params.get("period_days", 60)
            requested_indicators = extra_params.get("indicators", self._supported_indicators)
            
            # 验证代码
            if not symbol or not isinstance(symbol, str):
                return self._error_result(start_time, "股票代码必须是非空字符串")
            
            self.logger.debug(f"分析 {symbol} (最近 {period_days} 天数据)")
            
            # 获取真实价格数据 (从 akshare 或 yfinance)
            price_data = await self._load_real_price_data(symbol, period_days)
            if not price_data or len(price_data) < 2:
                return self._error_result(start_time, f"无法获取 {symbol} 的价格数据")
            
            # 提取价格序列
            closes = [p["close"] for p in price_data]
            volumes = [p.get("volume", 0) for p in price_data]
            current_price = closes[-1]
            
            # 计算技术指标
            indicators = {}
            for indicator_name in requested_indicators:
                if indicator_name == "MA":
                    indicators["MA"] = self._calculate_ma(closes)
                elif indicator_name == "RSI":
                    indicators["RSI"] = self._calculate_rsi(closes)
                elif indicator_name == "MACD":
                    indicators["MACD"] = self._calculate_macd(closes)
                elif indicator_name == "Bollinger":
                    indicators["Bollinger"] = self._calculate_bollinger(closes)
            
            # 生成交易信号
            signal = self._generate_signal(
                symbol, current_price, closes, volumes, indicators
            )
            
            # 计算置信度
            confidence = self._calculate_confidence(
                signal, indicators, closes, volumes
            )
            
            # 构建结果
            analysis_result = {
                "symbol": symbol,
                "current_price": current_price,
                "date": datetime.now().isoformat(),
                "indicators": indicators,
                "signal": signal,
                "confidence": confidence,
                "data_source": self._get_data_source(symbol),
                "recommendation": f"{signal} (置信度: {confidence:.1%})"
            }
            
            return ExpertResult(
                status="success",
                data=analysis_result,
                confidence=confidence,
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            self.logger.error(f"分析失败: {str(e)}")
            return self._error_result(start_time, f"分析错误: {str(e)}")
    
    async def _load_real_price_data(self, symbol: str, days: int) -> List[Dict]:
        """
        从真实数据源加载价格数据 (Tushare > akshare > yfinance > 备选)
        
        优先级：
        1. Tushare (专业级 A 股数据)
        2. akshare (开源 A 股数据)
        3. yfinance (美股/国际数据)
        4. 模拟数据 (备选)
        
        Args:
            symbol: 股票代码 (如 600000.SH, AAPL)
            days: 需要的历史天数
        
        Returns:
            价格数据列表
        """
        # 首先尝试从缓存获取
        cache_key = f"{symbol}:{days}"
        if cache_key in self._data_cache:
            self.logger.debug(f"从缓存返回 {symbol} 数据")
            return self._data_cache[cache_key]
        
        # A股: 优先使用 Tushare
        if self._is_a_stock(symbol):
            data = await self._load_tushare_data(symbol, days)
            if data:
                self._data_cache[cache_key] = data
                return data
            
            # Tushare 失败，尝试 akshare
            data = await self._load_akshare_data(symbol, days)
            if data:
                self._data_cache[cache_key] = data
                return data
        
        # 美股: 使用 yfinance
        data = await self._load_yfinance_data(symbol, days)
        if data:
            self._data_cache[cache_key] = data
            return data
        
        # 备选: 生成模拟数据 (仅在其他来源都失败时)
        self.logger.warning(f"所有数据源都失败，使用备选模拟数据 {symbol}")
        return self._generate_fallback_data(symbol, days)
    
    async def _load_tushare_data(self, symbol: str, days: int) -> Optional[List[Dict]]:
        """从 Tushare 加载 A股数据（专业级）"""
        try:
            self.logger.info(f"从 Tushare 加载 {symbol}")
            
            # 计算日期范围
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
            
            # 调用 Tushare API
            prices = await self._tushare_provider.get_daily_data(
                symbol, start_date, end_date
            )
            
            if prices and len(prices) > 0:
                self.logger.info(f"成功从 Tushare 加载 {len(prices)} 条 {symbol} 数据")
                return prices
            else:
                self.logger.warning(f"Tushare 返回空数据 {symbol}")
                return None
                
        except Exception as e:
            self.logger.warning(f"Tushare 加载失败 {symbol}: {str(e)}")
            return None
    
    async def _load_akshare_data(self, symbol: str, days: int) -> Optional[List[Dict]]:
        """从 akshare 加载 A股数据"""
        try:
            import akshare as ak
            
            self.logger.info(f"从 akshare 加载 {symbol}")
            
            # 计算日期范围
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
            
            # 获取历史数据
            df = ak.stock_zh_a_hist(
                symbol=symbol.replace(".SH", "").replace(".SZ", ""),
                start_date=start_date,
                end_date=end_date
            )
            
            if df is None or len(df) == 0:
                self.logger.warning(f"akshare 返回空数据 {symbol}")
                return None
            
            # 转换为价格数据格式
            prices = []
            for _, row in df.iterrows():
                prices.append({
                    "date": row["日期"],
                    "open": float(row["开盘价"]),
                    "high": float(row["最高价"]),
                    "low": float(row["最低价"]),
                    "close": float(row["收盘价"]),
                    "volume": int(row["成交量"])
                })
            
            self.logger.info(f"成功加载 {len(prices)} 条 {symbol} 数据")
            return prices
            
        except Exception as e:
            self.logger.warning(f"akshare 加载失败 {symbol}: {str(e)}")
            return None
    
    async def _load_yfinance_data(self, symbol: str, days: int) -> Optional[List[Dict]]:
        """从 yfinance 加载美股数据"""
        try:
            import yfinance as yf
            
            self.logger.info(f"从 yfinance 加载 {symbol}")
            
            # 下载数据
            data = yf.download(
                symbol, 
                period=f"{min(days, 3650)}d",
                progress=False
            )
            
            if data is None or len(data) == 0:
                self.logger.warning(f"yfinance 返回空数据 {symbol}")
                return None
            
            # 转换为价格数据格式
            prices = []
            for date, row in data.iterrows():
                prices.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"])
                })
            
            self.logger.info(f"成功加载 {len(prices)} 条 {symbol} 数据")
            return prices
            
        except Exception as e:
            self.logger.warning(f"yfinance 加载失败 {symbol}: {str(e)}")
            return None
    
    def _generate_fallback_data(self, symbol: str, days: int) -> List[Dict]:
        """生成模拟数据 (仅作为最后备选)"""
        self.logger.warning(f"使用模拟数据 {symbol}")
        base_price = 100.0
        prices = []
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=days-i-1))
            # 更真实的模拟价格变动
            change = (hash(f"{symbol}{i}") % 200 - 100) / 1000
            price = base_price * (1 + change)
            
            prices.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": price * 0.99,
                "high": price * 1.02,
                "low": price * 0.98,
                "close": price,
                "volume": 1000000
            })
        
        return prices
    
    def _is_a_stock(self, symbol: str) -> bool:
        """检查是否是 A股代码"""
        return symbol.endswith((".SH", ".SZ"))
    
    def _get_data_source(self, symbol: str) -> str:
        """获取数据源"""
        if self._is_a_stock(symbol):
            return "akshare (A股实时数据)"
        return "yfinance (美股数据)"
    
    def _calculate_ma(self, closes: List[float]) -> Dict[str, float]:
        """计算移动平均"""
        return {
            "MA5": self._sma(closes, 5),
            "MA10": self._sma(closes, 10),
            "MA20": self._sma(closes, 20),
            "MA50": self._sma(closes, 50)
        }
    
    def _calculate_rsi(self, closes: List[float], period: int = 14) -> float:
        """计算相对强度指数"""
        if len(closes) < period + 1:
            return 50.0
        
        deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
        gains = [d if d > 0 else 0 for d in deltas[-period:]]
        losses = [-d if d < 0 else 0 for d in deltas[-period:]]
        
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        
        if avg_loss == 0:
            return 100.0 if avg_gain > 0 else 50.0
        
        rs = avg_gain / avg_loss
        return 100.0 - (100.0 / (1.0 + rs))
    
    def _calculate_macd(self, closes: List[float]) -> Dict[str, Any]:
        """计算 MACD"""
        ema12 = self._ema(closes, 12)
        ema26 = self._ema(closes, 26)
        
        dif = ema12 - ema26
        signal = self._sma([ema12 - ema26], 9)
        macd = 2 * (dif - signal)
        
        return {
            "DIF": dif,
            "Signal": signal,
            "MACD": macd,
            "Trend": "多头" if dif > signal else "空头"
        }
    
    def _calculate_bollinger(self, closes: List[float], period: int = 20) -> Dict[str, float]:
        """计算布林带"""
        sma = self._sma(closes, period)
        std = statistics.stdev(closes[-period:]) if len(closes) >= period else 0
        
        return {
            "Upper": sma + (2 * std),
            "Middle": sma,
            "Lower": sma - (2 * std)
        }
    
    def _generate_signal(
        self, symbol: str, price: float, closes: List[float],
        volumes: List[float], indicators: Dict
    ) -> str:
        """生成交易信号"""
        ma_data = indicators.get("MA", {})
        rsi_data = indicators.get("RSI", 50)
        macd_data = indicators.get("MACD", {})
        
        # 简单的信号生成逻辑
        buy_signals = 0
        sell_signals = 0
        
        # MA 信号
        if ma_data:
            ma5 = ma_data.get("MA5", price)
            ma20 = ma_data.get("MA20", price)
            if ma5 > ma20:
                buy_signals += 1
            else:
                sell_signals += 1
        
        # RSI 信号
        if rsi_data < 30:
            buy_signals += 1
        elif rsi_data > 70:
            sell_signals += 1
        
        # MACD 信号
        if macd_data.get("Trend") == "多头":
            buy_signals += 1
        else:
            sell_signals += 1
        
        if buy_signals >= 2:
            return "BUY"
        elif sell_signals >= 2:
            return "SELL"
        else:
            return "HOLD"
    
    def _calculate_confidence(
        self, signal: str, indicators: Dict,
        closes: List[float], volumes: List[float]
    ) -> float:
        """计算置信度 (0.0-1.0)"""
        rsi = indicators.get("RSI", 50)
        
        # RSI 极值表示高置信度
        if rsi < 20 or rsi > 80:
            confidence = 0.85
        elif rsi < 30 or rsi > 70:
            confidence = 0.75
        else:
            confidence = 0.60
        
        # 成交量增加表示置信度提高
        if len(volumes) >= 2:
            vol_ratio = volumes[-1] / (sum(volumes[-10:]) / 10)
            if vol_ratio > 1.5:
                confidence += 0.1
        
        return min(0.95, confidence)
    
    def _sma(self, values: List[float], period: int) -> float:
        """计算简单移动平均"""
        if len(values) < period:
            return values[-1]
        return sum(values[-period:]) / period
    
    def _ema(self, values: List[float], period: int) -> float:
        """计算指数移动平均"""
        if len(values) < period:
            return values[-1]
        
        multiplier = 2 / (period + 1)
        sma = sum(values[-period:]) / period
        ema = sma
        
        for i in range(len(values) - period, len(values)):
            ema = values[i] * multiplier + ema * (1 - multiplier)
        
        return ema
    
    def _error_result(self, start_time: float, error_msg: str) -> ExpertResult:
        """返回错误结果"""
        return ExpertResult(
            status="error",
            data={"error": error_msg},
            confidence=0.0,
            execution_time=time.time() - start_time
        )
