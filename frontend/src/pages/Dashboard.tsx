import React, { useEffect, useMemo, useState } from 'react';
import StockChart from '../components/StockChart';
import { stockAPI, systemAPI } from '../services/api';

interface DashboardProps {
  user?: any;
}

/**
 * 主仪表板页面
 */
const Dashboard: React.FC<DashboardProps> = ({ user }) => {
  const cfoUrl = process.env.REACT_APP_CFO_URL || 'http://localhost:8501';
  const [stocks, setStocks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedStock, setSelectedStock] = useState('600000.SH');
  const [analysisResult, setAnalysisResult] = useState<any | null>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [health, setHealth] = useState<any | null>(null);
  const [experts, setExperts] = useState<any[]>([]);
  const [metrics, setMetrics] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);

  const stockExpertResult = useMemo(() => {
    if (!analysisResult?.expert_results) return null;
    return analysisResult.expert_results.find((r: any) => r.expert_name === 'StockAnalysisExpert') || null;
  }, [analysisResult]);

  const signal = stockExpertResult?.result?.signal ?? null;
  const confidence = stockExpertResult?.result?.confidence ?? null;
  const recommendation = stockExpertResult?.result?.recommendation ?? null;

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [healthResp, expertsResp, metricsResp, popular] = await Promise.all([
        systemAPI.health(),
        systemAPI.experts(),
        systemAPI.metrics(),
        stockAPI.getPopular(),
      ]);

      setHealth(healthResp);
      setExperts(expertsResp.experts || []);
      setMetrics(metricsResp);

      const symbols = popular.symbols || [];
      const cards = await Promise.all(
        symbols.slice(0, 6).map(async (symbol: string) => {
          const info = await stockAPI.getInfo(symbol);
          const hist = await stockAPI.getHistory(symbol, 2);
          const data = hist.data || [];
          const last = data.length > 0 ? data[data.length - 1].close : null;
          const prev = data.length > 1 ? data[data.length - 2].close : last;
          const change = last != null && prev != null && prev !== 0 ? ((last - prev) / prev) * 100 : 0;
          return {
            symbol,
            name: info?.name || symbol,
            price: last != null ? Number(last).toFixed(2) : '-',
            change: Number(change.toFixed(2)),
          };
        })
      );
      setStocks(cards);
    } catch (error: any) {
      setError(error?.message || '分析失败');
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeStock = async (symbol: string) => {
    try {
      setLoading(true);
      setSelectedStock(symbol);
      setError(null);

      const [hist, analysis] = await Promise.all([
        stockAPI.getHistory(symbol, 60),
        stockAPI.analyze(symbol, ['MA', 'RSI', 'MACD', 'Bollinger'], 60),
      ]);
      setHistory(hist.data || []);
      setAnalysisResult(analysis || null);
    } catch (error: any) {
      setError(error?.message || '分析失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-8">投资决策支持系统</h1>

      {error && (
        <div className="mb-8 bg-red-50 border border-red-200 text-red-700 rounded p-4">
          {error}
        </div>
      )}

      {/* 快速查询板块 */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-sm font-semibold text-gray-600 mb-2">系统健康</h3>
          <div className="text-2xl font-bold text-green-600">{health?.status || '-'}</div>
          <p className="text-xs text-gray-500 mt-2">version {health?.version || '-'}</p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-sm font-semibold text-gray-600 mb-2">已加载专家</h3>
          <div className="text-2xl font-bold text-blue-600">{experts.length}</div>
          <p className="text-xs text-gray-500 mt-2">/api/experts</p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-sm font-semibold text-gray-600 mb-2">请求统计</h3>
          <div className="text-2xl font-bold text-amber-600">{metrics?.total_requests ?? '-'}</div>
          <p className="text-xs text-gray-500 mt-2">success {metrics?.success_rate != null ? `${metrics.success_rate.toFixed(1)}%` : '-'}</p>
        </div>

        <a
          className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition block"
          href={cfoUrl}
          target="_blank"
          rel="noreferrer"
        >
          <h3 className="text-sm font-semibold text-gray-600 mb-2">子业务 / CFO 分析</h3>
          <div className="text-2xl font-bold text-purple-600">打开</div>
          <p className="text-xs text-gray-500 mt-2">新窗口打开多文档上传页</p>
        </a>
      </div>

      {/* 搜索和分析区域 */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">股票分析</h2>
        <div className="flex gap-4 mb-6">
          <input
            type="text"
            placeholder="输入股票代码 (如 600000.SH)"
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
            value={selectedStock}
            onChange={(e) => setSelectedStock(e.target.value)}
          />
          <button
            onClick={() => handleAnalyzeStock(selectedStock)}
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? '分析中...' : '分析'}
          </button>
        </div>

        {/* 分析结果 */}
        {analysisResult && (
          <div className="space-y-6">
            <StockChart
              data={history}
              title="技术面分析"
              symbol={selectedStock}
            />

            {/* 分析指标 */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-2">交易信号</p>
                <p className="text-lg font-bold text-blue-600">
                  {signal || '-'}
                </p>
              </div>

              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-2">置信度</p>
                <p className="text-lg font-bold text-green-600">
                  {confidence != null ? `${(confidence * 100).toFixed(1)}%` : '-'}
                </p>
              </div>

              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-2">风险等级</p>
                <p className="text-lg font-bold text-amber-600">
                  {analysisResult?.consensus_level || '-'}
                </p>
              </div>

              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-2">建议</p>
                <p className="text-sm font-semibold text-gray-800">
                  {recommendation || '-'}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 热门股票 */}
      {!loading && stocks.length > 0 && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">热门股票</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {stocks.map((stock, idx) => (
              <div
                key={idx}
                onClick={() => handleAnalyzeStock(stock.symbol)}
                className="p-4 border border-gray-200 rounded-lg cursor-pointer hover:shadow-md transition"
              >
                <p className="font-semibold text-lg">{stock.name}</p>
                <p className="text-sm text-gray-600">{stock.symbol}</p>
                <p className="text-lg font-bold text-green-600 mt-2">{stock.price}</p>
                <p className={`text-sm mt-1 ${stock.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {stock.change >= 0 ? '+' : ''}{stock.change}%
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
