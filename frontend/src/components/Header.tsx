import React, { useEffect, useState } from 'react';
import { clearApiToken, getApiToken, setApiToken, systemAPI } from '../services/api';

interface HeaderProps {
  user?: any;
}

/**
 * 页面头部组件
 */
const Header: React.FC<HeaderProps> = ({ user }) => {
  const [token, setToken] = useState(getApiToken());
  const [me, setMe] = useState<any | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refreshMe = async () => {
    try {
      setError(null);
      const data = await systemAPI.me();
      setMe(data);
    } catch (e: any) {
      setMe(null);
      setError(e?.message || '无法获取用户信息');
    }
  };

  useEffect(() => {
    refreshMe();
  }, []);

  const applyToken = async () => {
    setApiToken(token.trim());
    await refreshMe();
  };

  const removeToken = async () => {
    clearApiToken();
    setToken('');
    await refreshMe();
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="flex items-center justify-between px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold">SI</span>
          </div>
          <div>
            <p className="font-semibold text-gray-800">SiliconSoul MOE</p>
            <p className="text-xs text-gray-500">智能投资决策系统</p>
          </div>
        </div>

        <div className="flex items-center gap-6">
          <div className="hidden md:flex items-center gap-2">
            <input
              value={token}
              onChange={(e) => setToken(e.target.value)}
              placeholder="API Token"
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
            />
            <button
              onClick={applyToken}
              className="px-3 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700"
            >
              应用
            </button>
            <button
              onClick={removeToken}
              className="px-3 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm hover:bg-gray-200"
            >
              清除
            </button>
          </div>

          {/* 通知 */}
          <button className="relative text-gray-600 hover:text-blue-600">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            <span className="absolute top-0 right-0 w-2 h-2 bg-red-600 rounded-full"></span>
          </button>

          {/* 用户菜单 */}
          <div className="flex items-center gap-3 pl-6 border-l border-gray-200">
            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-semibold">JQ</span>
            </div>
            <div className="hidden sm:block">
              <p className="text-sm font-medium text-gray-800">{user?.name || '用户'}</p>
              <p className="text-xs text-gray-500">
                {error ? error : (me?.user_id ? `user_id: ${me.user_id}` : (user?.email || 'user@example.com'))}
              </p>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
