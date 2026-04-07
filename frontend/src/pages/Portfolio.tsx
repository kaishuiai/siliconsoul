import React from 'react';

interface PortfolioProps {
  user?: any;
}

/**
 * 投资组合管理页面
 */
const Portfolio: React.FC<PortfolioProps> = ({ user }) => {
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-8">投资组合</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-sm font-semibold text-gray-600 mb-2">总资产</h3>
          <p className="text-3xl font-bold text-blue-600">¥100,000</p>
          <p className="text-xs text-gray-500 mt-2">截至 2026-04-07</p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-sm font-semibold text-gray-600 mb-2">今日收益</h3>
          <p className="text-3xl font-bold text-green-600">+¥1,250</p>
          <p className="text-xs text-gray-500 mt-2">+1.25%</p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-sm font-semibold text-gray-600 mb-2">年度收益</h3>
          <p className="text-3xl font-bold text-green-600">+18.5%</p>
          <p className="text-xs text-gray-500 mt-2">累计收益</p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">持仓明细</h2>
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 text-left text-sm font-semibold text-gray-600">股票</th>
              <th className="px-4 py-2 text-right text-sm font-semibold text-gray-600">持仓</th>
              <th className="px-4 py-2 text-right text-sm font-semibold text-gray-600">成本价</th>
              <th className="px-4 py-2 text-right text-sm font-semibold text-gray-600">现价</th>
              <th className="px-4 py-2 text-right text-sm font-semibold text-gray-600">盈亏</th>
            </tr>
          </thead>
          <tbody>
            <tr className="border-b hover:bg-gray-50">
              <td className="px-4 py-3">浦发银行 (600000.SH)</td>
              <td className="px-4 py-3 text-right">1,000 股</td>
              <td className="px-4 py-3 text-right">¥10.50</td>
              <td className="px-4 py-3 text-right">¥10.85</td>
              <td className="px-4 py-3 text-right text-green-600">+¥350</td>
            </tr>
            <tr className="border-b hover:bg-gray-50">
              <td className="px-4 py-3">中国平安 (601318.SH)</td>
              <td className="px-4 py-3 text-right">500 股</td>
              <td className="px-4 py-3 text-right">¥18.20</td>
              <td className="px-4 py-3 text-right">¥18.95</td>
              <td className="px-4 py-3 text-right text-green-600">+¥375</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Portfolio;
