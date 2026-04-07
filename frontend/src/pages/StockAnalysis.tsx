import React, { useState } from 'react';
import StockChart from '../components/StockChart';

/**
 * 详细股票分析页面
 */
const StockAnalysis: React.FC = () => {
  const [symbol, setSymbol] = useState('600000.SH');
  const [period, setPeriod] = useState(60);

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
            <button className="w-full px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
              开始分析
            </button>
          </div>
        </div>
      </div>

      {/* 分析结果展示（占位符） */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* 主要图表 */}
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h3 className="text-lg font-semibold mb-4">技术指标分析</h3>
            <div className="h-64 flex items-center justify-center bg-gray-50 rounded">
              <p className="text-gray-500">图表加载中...</p>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold mb-4">支撑/阻力位</h3>
            <div className="space-y-2">
              <div className="flex justify-between p-2 border-b">
                <span className="text-gray-600">第一阻力位</span>
                <span className="font-semibold">¥10.85</span>
              </div>
              <div className="flex justify-between p-2 border-b">
                <span className="text-gray-600">第一支撑位</span>
                <span className="font-semibold">¥10.45</span>
              </div>
              <div className="flex justify-between p-2">
                <span className="text-gray-600">第二支撑位</span>
                <span className="font-semibold">¥10.10</span>
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
                <p className="text-sm text-gray-600">买入信号</p>
                <p className="font-semibold text-green-600">强烈看涨</p>
              </div>
              <div className="p-3 bg-blue-50 rounded border-l-4 border-blue-500">
                <p className="text-sm text-gray-600">置信度</p>
                <p className="font-semibold text-blue-600">82%</p>
              </div>
              <div className="p-3 bg-amber-50 rounded border-l-4 border-amber-500">
                <p className="text-sm text-gray-600">风险等级</p>
                <p className="font-semibold text-amber-600">中等</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold mb-4">关键指标</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">RSI</span>
                <span className="font-semibold">65</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">MACD</span>
                <span className="font-semibold">正</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">KDJ</span>
                <span className="font-semibold">75</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StockAnalysis;
