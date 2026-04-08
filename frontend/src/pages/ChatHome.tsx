import React, { useEffect, useMemo, useRef, useState } from 'react';
import { chatAPI, systemAPI } from '../services/api';

type Msg = {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  ts: string;
};

interface ChatHomeProps {
  user?: any;
}

const TASK_OPTIONS = [
  { label: '通用对话', value: 'dialog' },
  { label: 'CFO顾问', value: 'cfo_chat' },
  { label: '股票分析', value: 'stock_analysis' },
  { label: '知识问答', value: 'knowledge_qa' },
];

const toText = (obj: any): string => {
  if (obj == null) return '';
  if (typeof obj === 'string') return obj;
  if (typeof obj === 'number' || typeof obj === 'boolean') return String(obj);
  return JSON.stringify(obj, null, 2);
};

const extractAssistantText = (resp: any): string => {
  const fr = resp?.final_result || {};
  const candidates = [
    fr.answer,
    fr.response,
    fr.reply,
    fr.message,
    fr.summary,
    fr.recommendation,
    fr.final_decision,
    fr.analysis,
  ];
  for (const c of candidates) {
    const s = toText(c).trim();
    if (s) return s;
  }
  if (Array.isArray(resp?.expert_results) && resp.expert_results.length > 0) {
    const first = resp.expert_results.find((x: any) => !x?.error) || resp.expert_results[0];
    const s = toText(first?.result).trim();
    if (s) return s;
  }
  const fallback = toText(fr).trim();
  if (fallback) return fallback;
  return '已收到请求，但模型未返回可展示文本。';
};

const ChatHome: React.FC<ChatHomeProps> = ({ user }) => {
  const [messages, setMessages] = useState<Msg[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: '你好，我是 SiliconSoul AI 助手。你可以选择不同 Agent 与我对话。',
      ts: new Date().toISOString(),
    },
  ]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [taskType, setTaskType] = useState<string>('dialog');
  const [experts, setExperts] = useState<Array<{ name: string; supported_tasks: string[] }>>([]);
  const [expertName, setExpertName] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [conversationId] = useState<string>(() => `conv_${Date.now()}`);
  const listRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const res = await systemAPI.experts();
        setExperts((res?.experts || []).map((x: any) => ({ name: x.name, supported_tasks: x.supported_tasks || [] })));
      } catch {
      }
    })();
  }, []);

  useEffect(() => {
    if (!listRef.current) return;
    listRef.current.scrollTop = listRef.current.scrollHeight;
  }, [messages, sending]);

  const availableExperts = useMemo(() => {
    if (!taskType) return experts;
    return experts.filter((x) => Array.isArray(x.supported_tasks) && x.supported_tasks.includes(taskType));
  }, [experts, taskType]);

  const send = async () => {
    const text = input.trim();
    if (!text || sending) return;
    setError('');
    const userMsg: Msg = { id: `u_${Date.now()}`, role: 'user', content: text, ts: new Date().toISOString() };
    const nextMessages = [...messages, userMsg];
    setMessages(nextMessages);
    setInput('');
    setSending(true);
    try {
      const body: any = {
        text,
        task_type: taskType,
        user_id: user?.id || 'frontend_user',
        context: {
          conversation_id: conversationId,
          history: nextMessages.map((m) => ({ role: m.role, content: m.content, ts: m.ts })),
        },
      };
      if (expertName) body.expert_names = [expertName];
      const resp = await chatAPI.process(body);
      const assistantMsg: Msg = {
        id: `a_${Date.now()}`,
        role: 'assistant',
        content: extractAssistantText(resp),
        ts: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (e: any) {
      setError(e?.message || '发送失败');
      setMessages((prev) => [
        ...prev,
        {
          id: `err_${Date.now()}`,
          role: 'system',
          content: `请求失败：${e?.message || '未知错误'}`,
          ts: new Date().toISOString(),
        },
      ]);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="h-[calc(100vh-64px)] p-4 md:p-6 flex gap-4">
      <div className="w-80 shrink-0 bg-white rounded-lg shadow-md p-4 h-full overflow-auto">
        <h2 className="text-lg font-semibold mb-4">AI Agent</h2>
        <div className="mb-4">
          <div className="text-sm text-gray-600 mb-2">场景</div>
          <select
            value={taskType}
            onChange={(e) => setTaskType(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
          >
            {TASK_OPTIONS.map((x) => (
              <option key={x.value} value={x.value}>
                {x.label}
              </option>
            ))}
          </select>
        </div>
        <div className="mb-4">
          <div className="text-sm text-gray-600 mb-2">专家</div>
          <select
            value={expertName}
            onChange={(e) => setExpertName(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
          >
            <option value="">自动选择（推荐）</option>
            {availableExperts.map((x) => (
              <option key={x.name} value={x.name}>
                {x.name}
              </option>
            ))}
          </select>
        </div>
        <div className="text-xs text-gray-500">
          当前会话ID：{conversationId}
        </div>
      </div>
      <div className="flex-1 bg-white rounded-lg shadow-md flex flex-col min-w-0">
        <div className="px-6 py-4 border-b border-gray-200">
          <h1 className="text-xl font-semibold">AI 对话</h1>
          <div className="text-xs text-gray-500 mt-1">ChatGPT 风格多 Agent 对话首页</div>
        </div>
        <div ref={listRef} className="flex-1 overflow-auto px-6 py-4 space-y-4 bg-gray-50">
          {messages.map((m) => (
            <div key={m.id} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm whitespace-pre-wrap ${
                  m.role === 'user'
                    ? 'bg-blue-600 text-white'
                    : m.role === 'assistant'
                      ? 'bg-white border border-gray-200 text-gray-800'
                      : 'bg-amber-50 border border-amber-200 text-amber-800'
                }`}
              >
                {m.content}
              </div>
            </div>
          ))}
          {sending && (
            <div className="flex justify-start">
              <div className="bg-white border border-gray-200 text-gray-500 rounded-2xl px-4 py-3 text-sm">
                正在思考中...
              </div>
            </div>
          )}
        </div>
        <div className="border-t border-gray-200 p-4">
          {error && <div className="text-sm text-red-600 mb-2">{error}</div>}
          <div className="flex gap-3">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="输入你的问题，Enter 发送，Shift+Enter 换行"
              className="flex-1 h-24 resize-none px-4 py-3 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  send();
                }
              }}
            />
            <button
              onClick={send}
              disabled={sending || !input.trim()}
              className="self-end px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50"
            >
              发送
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatHome;
