import React, { useMemo, useState } from 'react';
import StockChart from '../components/StockChart';
import { stockAPI } from '../services/api';

/**
 * 详细股票分析页面
 */
const StockAnalysis: React.FC = () => {
  const [symbol, setSymbol] = useState('600000.SH');
  const [period, setPeriod] = useState(60);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [analysis, setAnalysis] = useState<any | null>(null);

  const stockExpertResult = useMemo(() => {
    if (!analysis?.expert_results) return null;
    return analysis.expert_results.find((r: any) => r.expert_name === 'StockAnalysisExpert') || null;
  }, [analysis]);

  const signal = stockExpertResult?.result?.signal ?? null;
  const confidence = stockExpertResult?.result?.confidence ?? null;
  const indicators = stockExpertResult?.result?.indicators ?? null;
  const levels = stockExpertResult?.result?.support_resistance ?? null;
  const trend = stockExpertResult?.result?.trend ?? null;

  const onAnalyze = async () => {
    setLoading(true);
    setError(null);
    try {
      const [historyResp, analyzeResp] = await Promise.all([
        stockAPI.getHistory(symbol, period),
        stockAPI.analyze(symbol, ['MA', 'RSI', 'MACD', 'Bollinger'], period),
      ]);
      setHistory(historyResp?.data || []);
      setAnalysis(analyzeResp || null);
    } catch (e: any) {
      setError(e?.message || '请求失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-8">详细股票分析</h1>

      {/* 参数设置 */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">分析参数</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              股票代码
            </label>
            <input
              type="text"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              placeholder="600000.SH"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              分析周期（天）
            </label>
            <select
              value={period}
              onChange={(e) => setPeriod(Number(e.target.value))}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg"
            >
              <option value={30}>近 1 个月</option>
              <option value={60}>近 3 个月</option>
              <option value={120}>近 6 个月</option>
              <option value={365}>近 1 年</option>
            </select>
          </div>

          <div className="flex items-end">
            <button
              className="w-full px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              onClick={onAnalyze}
              disabled={loading}
            >
              {loading ? '分析中...' : '开始分析'}
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="mb-8 bg-red-50 border border-red-200 text-red-700 rounded p-4">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* 主要图表 */}
        <div className="lg:col-span-2">
          <StockChart data={history} title="技术指标分析" symbol={symbol} />

          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold mb-4">支撑/阻力位</h3>
            <div className="space-y-2">
              <div className="flex justify-between p-2 border-b">
                <span className="text-gray-600">第一阻力位</span>
                <span className="font-semibold">
                  {levels?.resistance_1 != null ? levels.resistance_1.toFixed(2) : '-'}
                </span>
              </div>
              <div className="flex justify-between p-2 border-b">
                <span className="text-gray-600">第一支撑位</span>
                <span className="font-semibold">
                  {levels?.support_1 != null ? levels.support_1.toFixed(2) : '-'}
                </span>
              </div>
              <div className="flex justify-between p-2">
                <span className="text-gray-600">趋势</span>
                <span className="font-semibold">
                  {trend?.direction ? `${trend.direction} (${Math.round((trend.strength || 0) * 100)}%)` : '-'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* 指标面板 */}
        <div className="space-y-4">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold mb-4">交易信号</h3>
            <div className="space-y-3">
              <div className="p-3 bg-green-50 rounded border-l-4 border-green-500">
                <p className="text-sm text-gray-600">信号</p>
                <p className="font-semibold text-green-600">{signal || '-'}</p>
              </div>
              <div className="p-3 bg-blue-50 rounded border-l-4 border-blue-500">
                <p className="text-sm text-gray-600">置信度</p>
                <p className="font-semibold text-blue-600">
                  {confidence != null ? `${Math.round(confidence * 100)}%` : '-'}
                </p>
              </div>
              <div className="p-3 bg-amber-50 rounded border-l-4 border-amber-500">
                <p className="text-sm text-gray-600">一致性</p>
                <p className="font-semibold text-amber-600">{analysis?.consensus_level || '-'}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold mb-4">关键指标</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">RSI</span>
                <span className="font-semibold">{indicators?.RSI?.value ?? '-'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">MACD</span>
                <span className="font-semibold">{indicators?.MACD?.Histogram ?? '-'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">MA20</span>
                <span className="font-semibold">
                  {indicators?.MA?.MA20 != null ? indicators.MA.MA20.toFixed(2) : '-'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StockAnalysis;
