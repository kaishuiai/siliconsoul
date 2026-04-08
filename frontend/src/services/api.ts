import axios, { AxiosInstance } from 'axios';

/**
 * API 服务模块 - 与后端通信
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export const getApiToken = () => localStorage.getItem('api_token') || '';
export const setApiToken = (token: string) => localStorage.setItem('api_token', token);
export const clearApiToken = () => localStorage.removeItem('api_token');

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
    const token = getApiToken();
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
    return Promise.reject(error);
  }
);

type ApiSuccess<T> = {
  success?: boolean;
  status: 'success';
  data: T;
  timestamp?: string | number;
};

type ApiError = {
  success?: boolean;
  status: 'error';
  code?: number;
  message?: string;
  error?: { code?: number; message?: string };
  timestamp?: string | number;
};

const unwrap = <T>(resp: any): T => {
  if (resp && (resp.success === true || resp.status === 'success')) return (resp as ApiSuccess<T>).data;
  if (resp && (resp.success === false || resp.status === 'error')) {
    const err = resp as ApiError;
    throw new Error(err.message || err.error?.message || '请求失败');
  }
  return resp as T;
};

const get = async <T>(url: string, config?: any): Promise<T> => unwrap<T>(await api.get(url, config));
const post = async <T>(url: string, data?: any, config?: any): Promise<T> => unwrap<T>(await api.post(url, data, config));

/**
 * 股票分析 API
 */
export const stockAPI = {
  // 获取热门股票
  getPopular: () => get<{ symbols: string[] }>('/stocks/popular'),

  // 分析股票
  analyze: (
    symbol: string,
    indicators: string[] = ['MA', 'RSI', 'MACD'],
    periodDays: number = 60
  ) => post<any>('/analysis/analyze', { symbol, indicators, period_days: periodDays }),

  // 获取股票信息
  getInfo: (symbol: string) => get<{ symbol: string; name: string; market: string }>(`/stocks/${encodeURIComponent(symbol)}`),

  // 获取历史数据
  getHistory: (symbol: string, days: number = 60) =>
    get<{ symbol: string; days: number; data: any[] }>(`/stocks/${encodeURIComponent(symbol)}/history`, { params: { days } }),
};

/**
 * ML 预测 API
 */
export const mlAPI = {
  // 价格预测
  predictPrice: (symbol: string, prices: number[]) =>
    post<any>('/ml/predict-price', { symbol, prices }),

  // 异常检测
  detectAnomalies: (prices: number[]) =>
    post<any>('/ml/detect-anomalies', { prices }),

  // 风险评分
  calculateRisk: (prices: number[]) =>
    post<any>('/ml/calculate-risk', { prices }),

  // 情感分析
  analyzeSentiment: (prices: number[]) =>
    post<any>('/ml/analyze-sentiment', { prices }),
};

/**
 * 知识库 API
 */
export const knowledgeAPI = {
  // 搜索文章
  search: (query: string) =>
    get<any>('/knowledge/search', { params: { q: query } }),

  // 获取文章详情
  getArticle: (id: string) =>
    get<any>(`/knowledge/articles/${id}`),

  // 获取推荐
  getRecommendations: () =>
    get<any>('/knowledge/recommendations'),
};

/**
 * 投资组合 API
 */
export const portfolioAPI = {
  // 获取投资组合
  getPortfolio: (userId: string) =>
    get<any>(`/portfolio/${userId}`),

  // 更新持仓
  updatePosition: (userId: string, symbol: string, quantity: number) =>
    post<any>(`/portfolio/${userId}/positions`, { symbol, quantity }),

  // 获取统计
  getStats: (userId: string) =>
    get<any>(`/portfolio/${userId}/stats`),
};

export const systemAPI = {
  health: () => get<{ status: string; version: string; uptime?: string; request_count?: number }>('/health'),
  me: () => get<{ user_id: string; auth_enabled: boolean }>('/me'),
  experts: () => get<{ experts: Array<{ name: string; version: string; supported_tasks: string[] }> }>('/experts'),
  metrics: () => get<any>('/monitor/metrics'),
  monitorStatus: () => get<any>('/monitor/status'),
  stats: () => get<any>('/monitor/stats'),
  getConfig: () => get<any>('/config'),
  setConfig: (key: string, value: any) => post<any>('/config', { key, value }),
  getLLMSettings: () =>
    get<{ provider: string; api_base: string; model: string; has_api_key: boolean; api_key_tail?: string }>('/llm/settings'),
  setLLMSettings: (payload: { provider: string; api_key?: string; api_base?: string; model?: string }) =>
    post<any>('/llm/settings', payload),
};

export const chatAPI = {
  process: (body: {
    text: string;
    task_type?: string;
    context?: Record<string, any>;
    user_id?: string;
    extra_params?: Record<string, any>;
    expert_names?: string[];
  }, config?: any) => post<any>('/process', body, config),
  stream: async (
    body: {
      text: string;
      task_type?: string;
      context?: Record<string, any>;
      user_id?: string;
      extra_params?: Record<string, any>;
      expert_names?: string[];
    },
    onEvent: (evt: { event: string; data: any }) => void,
    signal?: AbortSignal
  ) => {
    const token = getApiToken();
    const resp = await fetch(`${API_BASE_URL}/process/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify(body),
      signal,
    });
    if (!resp.ok || !resp.body) {
      throw new Error(`流式请求失败: HTTP ${resp.status}`);
    }
    const reader = resp.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      let idx = buffer.indexOf('\n\n');
      while (idx >= 0) {
        const raw = buffer.slice(0, idx);
        buffer = buffer.slice(idx + 2);
        const lines = raw.split('\n');
        const eventLine = lines.find((x) => x.startsWith('event:')) || 'event: message';
        const dataLine = lines.find((x) => x.startsWith('data:')) || 'data: {}';
        const event = eventLine.replace('event:', '').trim();
        const dataText = dataLine.replace('data:', '').trim();
        let data: any = dataText;
        try {
          data = JSON.parse(dataText);
        } catch {
        }
        onEvent({ event, data });
        idx = buffer.indexOf('\n\n');
      }
    }
  },
};

export const historyAPI = {
  list: (
    userId: string,
    q: string = '',
    limit: number = 50,
    offset: number = 0,
    expertName: string = '',
    conversationId: string = '',
    replayOf: string = '',
    onlyReplay: boolean = false,
    consensusLevel: string = '',
    onlyErrors: boolean = false,
    since: string = '',
    until: string = '',
    taskType: string = ''
  ) =>
    get<{ items: Array<{ request_id: string; user_id: string; text: string; timestamp: string; conversation_id?: string; task_type?: string; replay_of?: string; consensus_level?: string; overall_confidence?: number }> }>(
      `/history/${encodeURIComponent(userId)}`,
      { params: { q, limit, offset, expert_name: expertName || undefined, conversation_id: conversationId || undefined, replay_of: replayOf || undefined, only_replay: onlyReplay || undefined, consensus_level: consensusLevel || undefined, only_errors: onlyErrors || undefined, since: since || undefined, until: until || undefined, task_type: taskType || undefined } }
    ),
  detail: (userId: string, requestId: string) =>
    get<any>(`/history/${encodeURIComponent(userId)}/${encodeURIComponent(requestId)}`),
  chain: (userId: string, requestId: string) =>
    get<any>(`/history/${encodeURIComponent(userId)}/${encodeURIComponent(requestId)}/chain`),
  roots: (
    userId: string,
    q: string = '',
    taskType: string = '',
    expertName: string = '',
    topN: number = 50,
    sortBy: 'latest' | 'risk' | 'depth' | 'activity' = 'latest'
  ) =>
    get<{ items: any[]; total_roots: number }>(
      `/history/roots/${encodeURIComponent(userId)}`,
      { params: { q: q || undefined, task_type: taskType || undefined, expert_name: expertName || undefined, top_n: topN, sort_by: sortBy } }
    ),
  replay: (
    userId: string,
    requestId: string,
    body?: { task_type?: string; expert_names?: string[] }
  ) =>
    post<any>(`/history/${encodeURIComponent(userId)}/${encodeURIComponent(requestId)}/replay`, body || {}),
};

export default api;
