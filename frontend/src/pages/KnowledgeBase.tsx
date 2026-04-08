import React, { useState } from 'react';
import { knowledgeAPI } from '../services/api';

/**
 * 知识库页面
 */
const KnowledgeBase: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any | null>(null);

  const onSearch = async () => {
    if (!searchQuery.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const resp = await knowledgeAPI.search(searchQuery);
      setResult(resp || null);
    } catch (e: any) {
      setError(e?.message || '搜索失败');
    } finally {
      setLoading(false);
    }
  };

  const articles = [
    {
      id: 1,
      title: '股票投资基础',
      description: '了解股票投资的基本概念和原理',
      views: 1024,
    },
    {
      id: 2,
      title: '技术分析指标详解',
      description: 'MA、RSI、MACD 等常用指标的应用',
      views: 2156,
    },
    {
      id: 3,
      title: '风险管理策略',
      description: '如何设置止损、管理头寸和资产配置',
      views: 1534,
    },
    {
      id: 4,
      title: '市场心理学',
      description: '理解市场参与者的情绪和行为模式',
      views: 892,
    },
  ];

  const filteredArticles = articles.filter(article =>
    article.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    article.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-8">知识库</h1>

      {/* 搜索 */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <div className="flex gap-3">
          <input
            type="text"
            placeholder="搜索知识库..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
          />
          <button
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            onClick={onSearch}
            disabled={loading}
          >
            {loading ? '搜索中...' : '智能搜索'}
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-8 bg-red-50 border border-red-200 text-red-700 rounded p-4">
          {error}
        </div>
      )}

      {result && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">检索结果</h2>
          <div className="text-sm text-gray-700 mb-4">
            {result.final_result?.error ? result.final_result.error : result.final_result?.summary || '已完成检索'}
          </div>
          <div className="space-y-3">
            {(result.expert_results || [])
              .filter((r: any) => r.expert_name === 'KnowledgeExpert' && r.result?.knowledge_items)
              .flatMap((r: any) => r.result.knowledge_items)
              .slice(0, 5)
              .map((item: any, idx: number) => (
                <div key={idx} className="border rounded p-3">
                  <div className="font-semibold">{item.title || item.source}</div>
                  <div className="text-gray-600 mt-1">{item.content}</div>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* 文章列表 */}
      <div className="grid grid-cols-1 gap-4">
        {filteredArticles.length > 0 ? (
          filteredArticles.map(article => (
            <div
              key={article.id}
              className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition cursor-pointer"
            >
              <h3 className="text-lg font-semibold text-blue-600 mb-2">{article.title}</h3>
              <p className="text-gray-600 mb-3">{article.description}</p>
              <div className="flex items-center justify-between text-sm text-gray-500">
                <span>👁️ {article.views} 次阅读</span>
                <span>→</span>
              </div>
            </div>
          ))
        ) : (
          <div className="text-center py-12 text-gray-500">
            <p>未找到相关文章</p>
          </div>
        )}
      </div>

      {/* 分类导航 */}
      <div className="mt-12">
        <h2 className="text-2xl font-semibold mb-6">分类浏览</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {['基础知识', '技术分析', '风险管理', '投资策略'].map((category, idx) => (
            <div
              key={idx}
              className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-6 cursor-pointer hover:shadow-md transition"
            >
              <p className="text-lg font-semibold text-blue-600">{category}</p>
              <p className="text-sm text-gray-600 mt-2">12 篇文章</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default KnowledgeBase;
