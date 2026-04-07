import axios, { AxiosInstance } from 'axios';

/**
 * API 服务模块 - 与后端通信
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// 创建 axios 实例
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 添加认证令牌
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

// 响应拦截器
api.interceptors.response.use(
  response => response.data,
  error => {
    if (error.response?.status === 401) {
      // 处理未授权
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

/**
 * 股票分析 API
 */
export const stockAPI = {
  // 获取热门股票
  getPopular: () => api.get('/stocks/popular'),

  // 分析股票
  analyze: (symbol: string, indicators: string[] = ['MA', 'RSI', 'MACD']) =>
    api.post('/analysis/analyze', { symbol, indicators }),

  // 获取股票信息
  getInfo: (symbol: string) => api.get(`/stocks/${symbol}`),

  // 获取历史数据
  getHistory: (symbol: string, days: number = 60) =>
    api.get(`/stocks/${symbol}/history`, { params: { days } }),
};

/**
 * ML 预测 API
 */
export const mlAPI = {
  // 价格预测
  predictPrice: (symbol: string, prices: number[]) =>
    api.post('/ml/predict-price', { symbol, prices }),

  // 异常检测
  detectAnomalies: (prices: number[]) =>
    api.post('/ml/detect-anomalies', { prices }),

  // 风险评分
  calculateRisk: (prices: number[]) =>
    api.post('/ml/calculate-risk', { prices }),

  // 情感分析
  analyzeSentiment: (prices: number[]) =>
    api.post('/ml/analyze-sentiment', { prices }),
};

/**
 * 知识库 API
 */
export const knowledgeAPI = {
  // 搜索文章
  search: (query: string) =>
    api.get('/knowledge/search', { params: { q: query } }),

  // 获取文章详情
  getArticle: (id: string) =>
    api.get(`/knowledge/articles/${id}`),

  // 获取推荐
  getRecommendations: () =>
    api.get('/knowledge/recommendations'),
};

/**
 * 投资组合 API
 */
export const portfolioAPI = {
  // 获取投资组合
  getPortfolio: (userId: string) =>
    api.get(`/portfolio/${userId}`),

  // 更新持仓
  updatePosition: (userId: string, symbol: string, quantity: number) =>
    api.post(`/portfolio/${userId}/positions`, { symbol, quantity }),

  // 获取统计
  getStats: (userId: string) =>
    api.get(`/portfolio/${userId}/stats`),
};

export default api;
