import React, { useEffect, useMemo, useRef, useState } from 'react';
import { chatAPI, historyAPI, systemAPI } from '../services/api';

type Msg = {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  ts: string;
};

type Session = {
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  taskType: string;
  expertName: string;
  archived?: boolean;
  messages: Msg[];
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

const STORE_KEY = 'chat_home_sessions_v1';
const DELETED_KEY = 'chat_home_deleted_sessions_v1';

const toText = (obj: any): string => {
  if (obj == null) return '';
  if (typeof obj === 'string') return obj;
  if (typeof obj === 'number' || typeof obj === 'boolean') return String(obj);
  return JSON.stringify(obj, null, 2);
};

const extractAssistantText = (resp: any): string => {
  const fr = resp?.final_result || {};
  const candidates = [fr.answer, fr.response, fr.reply, fr.message, fr.summary, fr.recommendation, fr.final_decision, fr.analysis];
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

const defaultWelcome = (): Msg => ({
  id: `welcome_${Date.now()}`,
  role: 'assistant',
  content: '你好，我是 SiliconSoul AI 助手。你可以选择不同 Agent 与我对话。',
  ts: new Date().toISOString(),
});

const makeSession = (): Session => {
  const now = new Date().toISOString();
  return {
    id: `conv_${Date.now()}_${Math.random().toString(16).slice(2, 6)}`,
    title: '新对话',
    createdAt: now,
    updatedAt: now,
    taskType: 'dialog',
    expertName: '',
    archived: false,
    messages: [defaultWelcome()],
  };
};

const ChatHome: React.FC<ChatHomeProps> = ({ user }) => {
  const [sessions, setSessions] = useState<Session[]>(() => {
    try {
      const raw = localStorage.getItem(STORE_KEY);
      if (!raw) return [makeSession()];
      const parsed = JSON.parse(raw);
      if (!Array.isArray(parsed) || parsed.length === 0) return [makeSession()];
      return parsed;
    } catch {
      return [makeSession()];
    }
  });
  const [activeId, setActiveId] = useState<string>(() => {
    try {
      const raw = localStorage.getItem(STORE_KEY);
      if (!raw) return '';
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed) && parsed.length > 0) return parsed[0].id;
      return '';
    } catch {
      return '';
    }
  });
  const [deletedSessionIds, setDeletedSessionIds] = useState<string[]>(() => {
    try {
      const raw = localStorage.getItem(DELETED_KEY);
      if (!raw) return [];
      const parsed = JSON.parse(raw);
      return Array.isArray(parsed) ? parsed.map((x) => String(x)) : [];
    } catch {
      return [];
    }
  });
  const [input, setInput] = useState('');
  const [sessionSearch, setSessionSearch] = useState('');
  const [sending, setSending] = useState(false);
  const [experts, setExperts] = useState<Array<{ name: string; supported_tasks: string[] }>>([]);
  const [error, setError] = useState('');
  const [lastDeleted, setLastDeleted] = useState<Session | null>(null);
  const listRef = useRef<HTMLDivElement | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const streamTimerRef = useRef<number | null>(null);
  const undoTimerRef = useRef<number | null>(null);

  useEffect(() => {
    if (!activeId && sessions.length > 0) setActiveId(sessions.find((x) => !x.archived)?.id || sessions[0].id);
  }, [activeId, sessions]);

  useEffect(() => {
    localStorage.setItem(STORE_KEY, JSON.stringify(sessions));
  }, [sessions]);
  useEffect(() => {
    localStorage.setItem(DELETED_KEY, JSON.stringify(deletedSessionIds));
  }, [deletedSessionIds]);

  useEffect(() => {
    (async () => {
      try {
        const res = await systemAPI.experts();
        setExperts((res?.experts || []).map((x: any) => ({ name: x.name, supported_tasks: x.supported_tasks || [] })));
      } catch {
      }
    })();
    return () => {
      if (streamTimerRef.current) window.clearInterval(streamTimerRef.current);
      if (undoTimerRef.current) window.clearTimeout(undoTimerRef.current);
      if (abortRef.current) abortRef.current.abort();
    };
  }, []);

  const visibleSessions = useMemo(
    () =>
      sessions
        .filter((x) => !x.archived)
        .filter((x) => {
          if (!sessionSearch.trim()) return true;
          const q = sessionSearch.trim().toLowerCase();
          const last = x.messages[x.messages.length - 1]?.content || '';
          return x.title.toLowerCase().includes(q) || last.toLowerCase().includes(q);
        })
        .sort((a, b) => (a.updatedAt < b.updatedAt ? 1 : -1)),
    [sessions, sessionSearch]
  );
  const activeSession = useMemo(() => sessions.find((x) => x.id === activeId) || visibleSessions[0] || null, [sessions, activeId, visibleSessions]);
  const messages = activeSession?.messages || [];

  useEffect(() => {
    if (!listRef.current) return;
    listRef.current.scrollTop = listRef.current.scrollHeight;
  }, [messages, sending]);

  const availableExperts = useMemo(() => {
    if (!activeSession) return [];
    if (!activeSession.taskType) return experts;
    return experts.filter((x) => Array.isArray(x.supported_tasks) && x.supported_tasks.includes(activeSession.taskType));
  }, [experts, activeSession]);

  const updateActiveSession = (updater: (s: Session) => Session) => {
    if (!activeSession) return;
    setSessions((prev) => prev.map((s) => (s.id === activeSession.id ? updater(s) : s)));
  };

  const streamToMessage = (messageId: string, fullText: string): Promise<void> =>
    new Promise((resolve) => {
      if (streamTimerRef.current) window.clearInterval(streamTimerRef.current);
      let index = 0;
      streamTimerRef.current = window.setInterval(() => {
        index += Math.max(1, Math.ceil(fullText.length / 120));
        const part = fullText.slice(0, index);
        setSessions((prev) =>
          prev.map((s) => ({
            ...s,
            messages: s.messages.map((m) => (m.id === messageId ? { ...m, content: part } : m)),
          }))
        );
        if (index >= fullText.length) {
          if (streamTimerRef.current) window.clearInterval(streamTimerRef.current);
          streamTimerRef.current = null;
          resolve();
        }
      }, 12);
    });

  const requestReply = async (text: string, historyMsgs: Msg[], appendUser: boolean) => {
    if (!activeSession || sending) return;
    setError('');
    const now = new Date().toISOString();
    let reqHistory = historyMsgs;
    if (appendUser) {
      const userMsg: Msg = { id: `u_${Date.now()}`, role: 'user', content: text, ts: now };
      reqHistory = [...historyMsgs, userMsg];
      updateActiveSession((s) => ({
        ...s,
        title: s.title === '新对话' ? text.slice(0, 20) : s.title,
        updatedAt: now,
        messages: reqHistory,
      }));
      setInput('');
    }

    const assistantId = `a_${Date.now()}`;
    updateActiveSession((s) => ({
      ...s,
      updatedAt: now,
      messages: [...reqHistory, { id: assistantId, role: 'assistant', content: '', ts: now }],
    }));

    setSending(true);
    try {
      abortRef.current = new AbortController();
      const body: any = {
        text,
        task_type: activeSession.taskType,
        user_id: user?.id || 'frontend_user',
        context: {
          conversation_id: activeSession.id,
          history: reqHistory.map((m) => ({ role: m.role, content: m.content, ts: m.ts })),
        },
      };
      if (activeSession.expertName) body.expert_names = [activeSession.expertName];
      try {
        await chatAPI.stream(
          body,
          ({ event, data }) => {
            if (event === 'delta') {
              const delta = typeof data?.delta === 'string' ? data.delta : '';
              if (!delta) return;
              setSessions((prev) =>
                prev.map((s) => ({
                  ...s,
                  messages: s.messages.map((m) => (m.id === assistantId ? { ...m, content: (m.content || '') + delta } : m)),
                }))
              );
            }
          },
          abortRef.current?.signal
        );
      } catch {
        const resp = await chatAPI.process(body, { signal: abortRef.current.signal });
        await streamToMessage(assistantId, extractAssistantText(resp));
      }
    } catch (e: any) {
      const isCanceled = e?.name === 'CanceledError' || e?.code === 'ERR_CANCELED' || /canceled/i.test(String(e?.message || ''));
      if (isCanceled) {
        updateActiveSession((s) => ({
          ...s,
          updatedAt: new Date().toISOString(),
          messages: s.messages.map((m) => (m.id === assistantId ? { ...m, role: 'system', content: '已停止生成' } : m)),
        }));
      } else {
        setError(e?.message || '发送失败');
        updateActiveSession((s) => ({
          ...s,
          updatedAt: new Date().toISOString(),
          messages: s.messages.map((m) => (m.id === assistantId ? { ...m, role: 'system', content: `请求失败：${e?.message || '未知错误'}` } : m)),
        }));
      }
    } finally {
      abortRef.current = null;
      setSending(false);
    }
  };

  const send = async () => {
    const text = input.trim();
    if (!text || !activeSession) return;
    await requestReply(text, activeSession.messages, true);
  };

  const stop = () => {
    if (abortRef.current) abortRef.current.abort();
    if (streamTimerRef.current) {
      window.clearInterval(streamTimerRef.current);
      streamTimerRef.current = null;
    }
  };

  const regenerate = async () => {
    if (!activeSession || sending) return;
    const msgs = activeSession.messages;
    let i = msgs.length - 1;
    while (i >= 0 && msgs[i].role !== 'user') i -= 1;
    if (i < 0) return;
    const lastUser = msgs[i];
    const base = msgs.slice(0, i + 1);
    updateActiveSession((s) => ({ ...s, messages: base, updatedAt: new Date().toISOString() }));
    await requestReply(lastUser.content, base, false);
  };

  const createNew = () => {
    const s = makeSession();
    setSessions((prev) => [s, ...prev]);
    setActiveId(s.id);
    setInput('');
    setError('');
  };

  const syncFromCloud = async () => {
    try {
      const uid = user?.id || 'frontend_user';
      const resp = await historyAPI.list(uid, '', 200, 0, '', '', '', false, '', false, '', '', '');
      const rows = Array.isArray(resp?.items) ? resp.items : [];
      const grouped = new Map<string, any[]>();
      for (const r of rows) {
        const cid = r.conversation_id || r.request_id;
        if (deletedSessionIds.includes(String(cid))) continue;
        if (!grouped.has(cid)) grouped.set(cid, []);
        grouped.get(cid)?.push(r);
      }
      const cloudSessions: Session[] = [];
      grouped.forEach((arr, cid) => {
        const sorted = [...arr].sort((a, b) => String(a.timestamp).localeCompare(String(b.timestamp)));
        const title = (sorted[0]?.text || '云端会话').slice(0, 20);
        const msgs: Msg[] = sorted.map((it, idx) => ({
          id: `${cid}_${idx}`,
          role: 'user',
          content: it.text || '',
          ts: it.timestamp || new Date().toISOString(),
        }));
        cloudSessions.push({
          id: String(cid),
          title,
          createdAt: sorted[0]?.timestamp || new Date().toISOString(),
          updatedAt: sorted[sorted.length - 1]?.timestamp || new Date().toISOString(),
          taskType: sorted[0]?.task_type || 'dialog',
          expertName: '',
          archived: false,
          messages: msgs.length > 0 ? msgs : [defaultWelcome()],
        });
      });
      if (cloudSessions.length > 0) {
        setSessions((prev) => {
          const map = new Map(prev.map((x) => [x.id, x]));
          for (const s of cloudSessions) map.set(s.id, s);
          return Array.from(map.values());
        });
      }
    } catch (e: any) {
      setError(e?.message || '云端同步失败');
    }
  };

  const renameCurrent = () => {
    if (!activeSession) return;
    const next = window.prompt('重命名会话', activeSession.title);
    if (!next || !next.trim()) return;
    updateActiveSession((s) => ({ ...s, title: next.trim(), updatedAt: new Date().toISOString() }));
  };

  const archiveCurrent = () => {
    if (!activeSession) return;
    updateActiveSession((s) => ({ ...s, archived: true, updatedAt: new Date().toISOString() }));
    const next = visibleSessions.find((x) => x.id !== activeSession.id);
    if (next) setActiveId(next.id);
    else {
      const s = makeSession();
      setSessions((prev) => [s, ...prev]);
      setActiveId(s.id);
    }
  };

  const deleteSession = (sessionId: string) => {
    const target = sessions.find((x) => x.id === sessionId);
    if (!target) return;
    const ok = window.confirm(`确认删除会话「${target.title || '新对话'}」？删除后不可恢复。`);
    if (!ok) return;
    if (sending && activeSession?.id === sessionId) stop();
    setSessions((prev) => prev.filter((x) => x.id !== sessionId));
    setDeletedSessionIds((prev) => (prev.includes(sessionId) ? prev : [sessionId, ...prev].slice(0, 1000)));
    setLastDeleted(target);
    if (undoTimerRef.current) window.clearTimeout(undoTimerRef.current);
    undoTimerRef.current = window.setTimeout(() => {
      setLastDeleted(null);
      undoTimerRef.current = null;
    }, 8000);
    if (activeId === sessionId) {
      const remain = sessions.filter((x) => x.id !== sessionId && !x.archived);
      if (remain.length > 0) {
        setActiveId(remain[0].id);
      } else {
        const s = makeSession();
        setSessions((prev) => [s, ...prev.filter((x) => x.id !== sessionId)]);
        setActiveId(s.id);
      }
    }
  };

  const undoDelete = () => {
    if (!lastDeleted) return;
    if (undoTimerRef.current) {
      window.clearTimeout(undoTimerRef.current);
      undoTimerRef.current = null;
    }
    setSessions((prev) => {
      if (prev.some((x) => x.id === lastDeleted.id)) return prev;
      return [lastDeleted, ...prev];
    });
    setDeletedSessionIds((prev) => prev.filter((x) => x !== lastDeleted.id));
    setActiveId(lastDeleted.id);
    setLastDeleted(null);
  };

  return (
    <div className="h-[calc(100vh-64px)] p-4 md:p-6 flex gap-4">
      <div className="w-80 shrink-0 bg-white rounded-lg shadow-md p-4 h-full overflow-auto">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold">会话</h2>
          <div className="flex items-center gap-2">
            <button onClick={syncFromCloud} className="px-2 py-1 border text-xs rounded text-gray-700 hover:bg-gray-50">云端同步</button>
            <button onClick={createNew} className="px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700">新建</button>
          </div>
        </div>
        <input
          value={sessionSearch}
          onChange={(e) => setSessionSearch(e.target.value)}
          placeholder="搜索会话"
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm mb-3"
        />
        <div className="space-y-2 max-h-64 overflow-auto mb-4">
          {visibleSessions.map((s) => (
            <div
              key={s.id}
              className={`w-full text-left px-3 py-2 border rounded-lg ${activeSession?.id === s.id ? 'border-blue-300 bg-blue-50' : 'border-gray-200 bg-white hover:bg-gray-50'}`}
            >
              <button onClick={() => setActiveId(s.id)} className="w-full text-left">
                <div className="text-sm font-semibold text-gray-800 truncate">{s.title || '新对话'}</div>
                <div className="text-xs text-gray-500 truncate">{new Date(s.updatedAt).toLocaleString()}</div>
              </button>
              <div className="mt-1 flex justify-end">
                <button
                  onClick={() => deleteSession(s.id)}
                  className="text-xs px-2 py-1 border border-red-200 text-red-600 rounded hover:bg-red-50"
                >
                  删除
                </button>
              </div>
            </div>
          ))}
        </div>
        <div className="flex gap-2 mb-4">
          <button onClick={renameCurrent} disabled={!activeSession} className="px-2 py-1 border rounded text-xs text-gray-700 disabled:opacity-40">重命名</button>
          <button onClick={archiveCurrent} disabled={!activeSession} className="px-2 py-1 border rounded text-xs text-gray-700 disabled:opacity-40">归档</button>
          <button onClick={() => activeSession && deleteSession(activeSession.id)} disabled={!activeSession} className="px-2 py-1 border rounded text-xs text-red-600 border-red-200 disabled:opacity-40">删除</button>
        </div>
        <div className="mb-4">
          <div className="text-sm text-gray-600 mb-2">场景</div>
          <select
            value={activeSession?.taskType || 'dialog'}
            onChange={(e) => updateActiveSession((s) => ({ ...s, taskType: e.target.value, expertName: '' }))}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
          >
            {TASK_OPTIONS.map((x) => (
              <option key={x.value} value={x.value}>{x.label}</option>
            ))}
          </select>
        </div>
        <div className="mb-2">
          <div className="text-sm text-gray-600 mb-2">专家</div>
          <select
            value={activeSession?.expertName || ''}
            onChange={(e) => updateActiveSession((s) => ({ ...s, expertName: e.target.value }))}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
          >
            <option value="">自动选择（推荐）</option>
            {availableExperts.map((x) => (
              <option key={x.name} value={x.name}>{x.name}</option>
            ))}
          </select>
        </div>
        <div className="text-xs text-gray-500">会话ID：{activeSession?.id || '-'}</div>
      </div>

      <div className="flex-1 bg-white rounded-lg shadow-md flex flex-col min-w-0">
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold">AI 对话</h1>
            <div className="text-xs text-gray-500 mt-1">多会话 / 多 Agent / 可停止与重生成</div>
          </div>
          <div className="flex gap-2">
            <button onClick={regenerate} disabled={sending || !activeSession} className="px-3 py-2 border rounded text-sm text-gray-700 disabled:opacity-40">重新生成</button>
            <button onClick={stop} disabled={!sending} className="px-3 py-2 border rounded text-sm text-red-600 border-red-200 disabled:opacity-40">停止生成</button>
          </div>
        </div>

        <div ref={listRef} className="flex-1 overflow-auto px-6 py-4 space-y-4 bg-gray-50">
          {messages.map((m) => (
            <div key={m.id} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm whitespace-pre-wrap ${
                m.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : m.role === 'assistant'
                    ? 'bg-white border border-gray-200 text-gray-800'
                    : 'bg-amber-50 border border-amber-200 text-amber-800'
              }`}>
                {m.content || (sending && m.role === 'assistant' ? '...' : '')}
              </div>
            </div>
          ))}
          {sending && (
            <div className="flex justify-start">
              <div className="bg-white border border-gray-200 text-gray-500 rounded-2xl px-4 py-3 text-sm">
                正在生成中...
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
            <button onClick={send} disabled={sending || !input.trim() || !activeSession} className="self-end px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50">
              发送
            </button>
          </div>
        </div>
      </div>
      {lastDeleted && (
        <div className="fixed bottom-6 right-6 bg-gray-900 text-white px-4 py-3 rounded-lg shadow-lg flex items-center gap-3">
          <span className="text-sm">已删除「{lastDeleted.title || '新对话'}」</span>
          <button onClick={undoDelete} className="text-sm px-2 py-1 rounded bg-white text-gray-900 hover:bg-gray-100">
            撤销
          </button>
        </div>
      )}
    </div>
  );
};

export default ChatHome;
