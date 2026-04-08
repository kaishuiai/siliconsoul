import React, { useEffect, useMemo, useState } from 'react';
import { portfolioAPI, stockAPI } from '../services/api';

interface PortfolioProps {
  user?: any;
}

/**
 * 投资组合管理页面
 */
const Portfolio: React.FC<PortfolioProps> = ({ user }) => {
  const userId = useMemo(() => user?.id || user?.user_id || 'demo_user', [user]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [positions, setPositions] = useState<Array<{ symbol: string; quantity: number; updated_at?: string }>>([]);
  const [stats, setStats] = useState<any | null>(null);
  const [prices, setPrices] = useState<Record<string, number>>({});

  const [newSymbol, setNewSymbol] = useState('600000.SH');
  const [newQuantity, setNewQuantity] = useState(100);

  const loadAll = async () => {
    setLoading(true);
    setError(null);
    try {
      const [portfolio, st] = await Promise.all([
        portfolioAPI.getPortfolio(userId),
        portfolioAPI.getStats(userId),
      ]);
      const pos = portfolio.positions || [];
      setPositions(pos);
      setStats(st);

      const pricePairs = await Promise.all(
        pos.slice(0, 20).map(async (p: any) => {
          const hist = await stockAPI.getHistory(p.symbol, 2);
          const data = hist.data || [];
          const last = data.length > 0 ? Number(data[data.length - 1].close) : 0;
          return [p.symbol, last] as const;
        })
      );
      const next: Record<string, number> = {};
      for (const [sym, pr] of pricePairs) next[sym] = pr;
      setPrices(next);
    } catch (e: any) {
      setError(e?.message || '加载失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAll();
  }, [userId]);

  const onUpdate = async () => {
    setLoading(true);
    setError(null);
    try {
      await portfolioAPI.updatePosition(userId, newSymbol, newQuantity);
      await loadAll();
    } catch (e: any) {
      setError(e?.message || '更新失败');
    } finally {
      setLoading(false);
    }
  };

  const totalValue = useMemo(() => {
    return positions.reduce((sum, p) => sum + (prices[p.symbol] || 0) * (p.quantity || 0), 0);
  }, [positions, prices]);

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-8">投资组合</h1>

      {error && (
        <div className="mb-8 bg-red-50 border border-red-200 text-red-700 rounded p-4">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-sm font-semibold text-gray-600 mb-2">总资产</h3>
          <p className="text-3xl font-bold text-blue-600">¥{totalValue.toFixed(2)}</p>
          <p className="text-xs text-gray-500 mt-2">截至 2026-04-07</p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-sm font-semibold text-gray-600 mb-2">持仓数量</h3>
          <p className="text-3xl font-bold text-green-600">{stats?.positions_count ?? '-'}</p>
          <p className="text-xs text-gray-500 mt-2">合计份额 {stats?.total_quantity ?? '-'}</p>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-sm font-semibold text-gray-600 mb-2">用户</h3>
          <p className="text-3xl font-bold text-green-600">{userId}</p>
          <p className="text-xs text-gray-500 mt-2">Portfolio API</p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">更新持仓</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm text-gray-600 mb-2">股票代码</label>
            <input
              type="text"
              value={newSymbol}
              onChange={(e) => setNewSymbol(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-600 mb-2">数量</label>
            <input
              type="number"
              value={newQuantity}
              onChange={(e) => setNewQuantity(parseInt(e.target.value || '0', 10))}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={onUpdate}
              disabled={loading}
              className="w-full px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? '处理中...' : '保存'}
            </button>
          </div>
        </div>
        <div className="text-xs text-gray-500 mt-3">数量为 0 会删除该持仓</div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-semibold mb-4">持仓明细</h2>
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 text-left text-sm font-semibold text-gray-600">股票</th>
              <th className="px-4 py-2 text-right text-sm font-semibold text-gray-600">持仓</th>
              <th className="px-4 py-2 text-right text-sm font-semibold text-gray-600">现价</th>
              <th className="px-4 py-2 text-right text-sm font-semibold text-gray-600">市值</th>
            </tr>
          </thead>
          <tbody>
            {positions.length === 0 ? (
              <tr>
                <td className="px-4 py-3 text-gray-500" colSpan={4}>
                  暂无持仓
                </td>
              </tr>
            ) : (
              positions.map((p) => {
                const price = prices[p.symbol];
                const value = (price || 0) * (p.quantity || 0);
                return (
                  <tr key={p.symbol} className="border-b hover:bg-gray-50">
                    <td className="px-4 py-3">{p.symbol}</td>
                    <td className="px-4 py-3 text-right">{p.quantity}</td>
                    <td className="px-4 py-3 text-right">{price ? `¥${price.toFixed(2)}` : '-'}</td>
                    <td className="px-4 py-3 text-right">{price ? `¥${value.toFixed(2)}` : '-'}</td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Portfolio;
