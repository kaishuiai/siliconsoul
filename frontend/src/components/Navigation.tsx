import React from 'react';
import { Link, useLocation } from 'react-router-dom';

/**
 * 侧边栏导航组件
 */
const Navigation: React.FC = () => {
  const location = useLocation();

  const isActive = (path: string) => {
    return location.pathname === path ? 'bg-blue-50 text-blue-600' : 'text-gray-700 hover:bg-gray-50';
  };

  return (
    <nav className="w-64 bg-white shadow-md min-h-screen p-6">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-blue-600">SiliconSoul</h1>
        <p className="text-xs text-gray-500">投资决策系统</p>
      </div>

      <ul className="space-y-2">
        <li>
          <Link
            to="/"
            className={`block px-4 py-2 rounded-lg transition ${isActive('/')}`}
          >
            📊 仪表板
          </Link>
        </li>
        <li>
          <Link
            to="/stock-analysis"
            className={`block px-4 py-2 rounded-lg transition ${isActive('/stock-analysis')}`}
          >
            📈 股票分析
          </Link>
        </li>
        <li>
          <Link
            to="/portfolio"
            className={`block px-4 py-2 rounded-lg transition ${isActive('/portfolio')}`}
          >
            💼 投资组合
          </Link>
        </li>
        <li>
          <Link
            to="/knowledge"
            className={`block px-4 py-2 rounded-lg transition ${isActive('/knowledge')}`}
          >
            📚 知识库
          </Link>
        </li>
      </ul>

      <div className="mt-12 pt-6 border-t border-gray-200">
        <h3 className="text-sm font-semibold text-gray-600 mb-4">最近查看</h3>
        <ul className="space-y-2 text-sm">
          <li className="text-gray-500 hover:text-blue-600 cursor-pointer">600000.SH</li>
          <li className="text-gray-500 hover:text-blue-600 cursor-pointer">000858.SZ</li>
          <li className="text-gray-500 hover:text-blue-600 cursor-pointer">601888.SH</li>
        </ul>
      </div>
    </nav>
  );
};

export default Navigation;
