import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';

// Components
import ChatHome from './pages/ChatHome';
import Dashboard from './pages/Dashboard';
import StockAnalysis from './pages/StockAnalysis';
import Portfolio from './pages/Portfolio';
import KnowledgeBase from './pages/KnowledgeBase';
import History from './pages/History';
import Navigation from './components/Navigation';
import Header from './components/Header';
import { systemAPI } from './services/api';

/**
 * SiliconSoul MOE - 主应用程序
 */
function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    // 初始化用户信息
    const initializeApp = async () => {
      try {
        setIsLoading(true);
        // 从本地存储或 API 获取用户信息
        const savedUser = localStorage.getItem('user');
        if (savedUser) {
          setUser(JSON.parse(savedUser));
        }
        try {
          const me = await systemAPI.me();
          if (me?.user_id) {
            const u = { id: me.user_id, name: me.user_id, email: '' };
            setUser(u as any);
            localStorage.setItem('user', JSON.stringify(u));
          }
        } catch {
        }
      } catch (error) {
        console.error('应用初始化失败:', error);
      } finally {
        setIsLoading(false);
      }
    };

    initializeApp();
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">加载中...</p>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Header user={user} />
        <div className="flex">
          <Navigation />
          <main className="flex-1 overflow-auto">
            <Routes>
              <Route path="/" element={<ChatHome user={user} />} />
              <Route path="/dashboard" element={<Dashboard user={user} />} />
              <Route path="/stock-analysis" element={<StockAnalysis />} />
              <Route path="/portfolio" element={<Portfolio user={user} />} />
              <Route path="/knowledge" element={<KnowledgeBase />} />
              <Route path="/history" element={<History />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;
