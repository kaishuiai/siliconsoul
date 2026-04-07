import React, { useState, useEffect } from 'react';
import axios from 'axios';
import StockChart from '../components/StockChart';

interface DashboardProps {
  user?: any;
}

/**
 * 主仪表板页面
 */
const Dashboard: React.FC<DashboardProps> = ({ user }) => {
  const [stocks, setStocks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedStock, setSelectedStock] = useState('600000.SH');
  const [analysisResult, setAnalysisResult] = useState(null);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      // 加载初始股票数据
      const response = await axios.get('/api/stocks/popular');
      setStocks(response.data.stocks);
    } catch (error) {
      console.error('加载数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeStock = async (symbol: string) => {
    try {
      setLoading(true);
      setSelectedStock(symbol);
      
      // 调用分析接口
      const response = await axios.post('/api/analysis/analyze', {
        symbol,
        indicators: ['MA', 'RSI', 'MACD', 'Bollinger'],
      });
      
      setAnalysisResult(response.data);
    } catch (error) {
      console.error('分析失败:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-8">投资决策支持系统</h1>

      {/* 快速查询板块 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-sm font-semibold text-gray-600 mb-2">今日涨幅TOP</h3>
          <div className="text-2xl font-bold text-green-600">+3.5%</div>
          <p className="text-xs text-gray-500 mt-2">平均涨幅</p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-sm font-semibold text-gray-600 mb-2">市场热度</h3>
          <div className="text-2xl font-bold text-blue-600">7.2/10</div>
          <p className="text-xs text-gray-500 mt-2">较高热度</p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-sm font-semibold text-gray-600 mb-2">投资机会</h3>
          <div className="text-2xl font-bold text-amber-600">24</div>
          <p className="text-xs text-gray-500 mt-2">推荐股票</p>
        </div>
      </div>

      {/* 搜索和分析区域 */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">股票分析</h2>
        <div className="flex gap-4 mb-6">
          <input
            type="text"
            placeholder="输入股票代码 (如 600000.SH)"
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
            defaultValue={selectedStock}
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
              data={analysisResult.price_data}
              title="技术面分析"
              symbol={selectedStock}
            />

            {/* 分析指标 */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-2">交易信号</p>
                <p className="text-lg font-bold text-blue-600">
                  {analysisResult.signal}
                </p>
              </div>

              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-2">置信度</p>
                <p className="text-lg font-bold text-green-600">
                  {(analysisResult.confidence * 100).toFixed(1)}%
                </p>
              </div>

              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-2">风险等级</p>
                <p className="text-lg font-bold text-amber-600">
                  中等
                </p>
              </div>

              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-600 mb-2">建议</p>
                <p className="text-sm font-semibold text-gray-800">
                  {analysisResult.recommendation}
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
