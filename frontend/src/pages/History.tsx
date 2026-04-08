import React, { useEffect, useMemo, useState } from 'react';
import { historyAPI, systemAPI } from '../services/api';

const History: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [userId, setUserId] = useState<string>('demo_user');
  const [q, setQ] = useState<string>('');
  const [expertName, setExpertName] = useState<string>('');
  const [taskType, setTaskType] = useState<string>('');
  const [onlyCFO, setOnlyCFO] = useState<boolean>(false);
  const [consensusLevel, setConsensusLevel] = useState<string>('');
  const [onlyErrors, setOnlyErrors] = useState<boolean>(false);
  const [limit, setLimit] = useState<number>(50);
  const [offset, setOffset] = useState<number>(0);
  const [timeRange, setTimeRange] = useState<string>('');
  const [items, setItems] = useState<any[]>([]);
  const [selected, setSelected] = useState<any | null>(null);
  const [expertOptions, setExpertOptions] = useState<string[]>([]);
  const [detailExpertName, setDetailExpertName] = useState<string>('');
  const [detailOnlyErrors, setDetailOnlyErrors] = useState<boolean>(false);
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({});
  const [replayTaskType, setReplayTaskType] = useState<string>('');
  const [replayExperts, setReplayExperts] = useState<string[]>([]);
  const [compareOld, setCompareOld] = useState<any | null>(null);
  const [compareNew, setCompareNew] = useState<any | null>(null);
  const [diffView, setDiffView] = useState<'all' | 'summary' | 'final_result'>('all');
  const [diffKinds, setDiffKinds] = useState<Record<DiffKind, boolean>>({
    added: true,
    removed: true,
    changed: true,
    type_changed: true,
  });
  const [diffOnlyConfidenceDelta, setDiffOnlyConfidenceDelta] = useState<boolean>(false);
  const [diffConfidenceThresholdPct, setDiffConfidenceThresholdPct] = useState<number>(10);

  const canQuery = useMemo(() => !!userId, [userId]);

  const aggregated = useMemo(() => {
    if (selected?.aggregated) return selected.aggregated;
    if (!selected?.results) return null;
    return selected.results.find((r: any) => r.expert_name === '__aggregated__') || null;
  }, [selected]);

  const compareOldAgg = useMemo(() => {
    if (!compareOld) return null;
    if (compareOld?.aggregated) return compareOld.aggregated;
    if (!compareOld?.results) return null;
    return compareOld.results.find((r: any) => r.expert_name === '__aggregated__') || null;
  }, [compareOld]);

  const compareNewAgg = useMemo(() => {
    if (!compareNew) return null;
    if (compareNew?.aggregated) return compareNew.aggregated;
    if (!compareNew?.results) return null;
    return compareNew.results.find((r: any) => r.expert_name === '__aggregated__') || null;
  }, [compareNew]);

  const expertResults = useMemo(() => {
    if (!selected?.results) return [];
    return selected.results.filter((r: any) => r.expert_name !== '__aggregated__');
  }, [selected]);

  const filteredDetailResults = useMemo(() => {
    let rs = expertResults;
    if (detailExpertName) {
      rs = rs.filter((r: any) => r.expert_name === detailExpertName);
    }
    if (detailOnlyErrors) {
      rs = rs.filter((r: any) => !!r.error);
    }
    return rs;
  }, [expertResults, detailExpertName, detailOnlyErrors]);

  const hasNextPage = useMemo(() => items.length === limit, [items, limit]);

  const computeSinceUntil = () => {
    const now = new Date();
    if (timeRange === '24h') {
      return { since: new Date(now.getTime() - 24 * 3600 * 1000).toISOString(), until: '' };
    }
    if (timeRange === '7d') {
      return { since: new Date(now.getTime() - 7 * 24 * 3600 * 1000).toISOString(), until: '' };
    }
    if (timeRange === '30d') {
      return { since: new Date(now.getTime() - 30 * 24 * 3600 * 1000).toISOString(), until: '' };
    }
    return { since: '', until: '' };
  };

  type DiffKind = 'added' | 'removed' | 'changed' | 'type_changed';
  type DiffEntry = { path: string; kind: DiffKind; oldValue: any; newValue: any };

  const isPlainObject = (v: any) => v !== null && typeof v === 'object' && !Array.isArray(v);

  const toPreview = (v: any) => {
    const s = v === undefined ? 'undefined' : JSON.stringify(v);
    if (!s) return '';
    return s.length > 140 ? `${s.slice(0, 140)}...` : s;
  };

  const escapeMdCell = (s: string) => s.replace(/\|/g, '\\|').replace(/\n/g, ' ');

  const buildDiffMarkdown = (entries: DiffEntry[]) => {
    const rows = entries.map((d) => {
      const path = escapeMdCell(d.path || '(root)');
      const kind = escapeMdCell(d.kind);
      const oldStr = escapeMdCell(toPreview(d.oldValue));
      const newStr = escapeMdCell(toPreview(d.newValue));
      return `| ${path} | ${kind} | ${oldStr} | ${newStr} |`;
    });
    return [
      '# Compare Changes',
      '',
      '| path | kind | old | new |',
      '| --- | --- | --- | --- |',
      ...rows,
      '',
    ].join('\n');
  };

  const diffAny = (oldValue: any, newValue: any, path: string, out: DiffEntry[], depth: number, maxDiffs: number) => {
    if (out.length >= maxDiffs) return;
    if (depth <= 0) {
      if (JSON.stringify(oldValue) !== JSON.stringify(newValue)) {
        out.push({ path, kind: 'changed', oldValue, newValue });
      }
      return;
    }

    const oldIsArr = Array.isArray(oldValue);
    const newIsArr = Array.isArray(newValue);
    const oldIsObj = isPlainObject(oldValue);
    const newIsObj = isPlainObject(newValue);

    if (oldValue === undefined && newValue !== undefined) {
      out.push({ path, kind: 'added', oldValue, newValue });
      return;
    }
    if (oldValue !== undefined && newValue === undefined) {
      out.push({ path, kind: 'removed', oldValue, newValue });
      return;
    }

    if (oldIsArr !== newIsArr || oldIsObj !== newIsObj) {
      if (JSON.stringify(oldValue) !== JSON.stringify(newValue)) {
        out.push({ path, kind: 'type_changed', oldValue, newValue });
      }
      return;
    }

    if (oldIsArr && newIsArr) {
      const maxLen = Math.max(oldValue.length, newValue.length);
      for (let i = 0; i < maxLen && out.length < maxDiffs; i++) {
        diffAny(oldValue[i], newValue[i], `${path}[${i}]`, out, depth - 1, maxDiffs);
      }
      return;
    }

    if (oldIsObj && newIsObj) {
      const keys = new Set<string>([...Object.keys(oldValue), ...Object.keys(newValue)]);
      for (const k of Array.from(keys).sort()) {
        if (out.length >= maxDiffs) break;
        const nextPath = path ? `${path}.${k}` : k;
        diffAny(oldValue[k], newValue[k], nextPath, out, depth - 1, maxDiffs);
      }
      return;
    }

    if (JSON.stringify(oldValue) !== JSON.stringify(newValue)) {
      out.push({ path, kind: 'changed', oldValue, newValue });
    }
  };

  const diffSummaryAll = useMemo(() => {
    const oldAgg = compareOldAgg?.result || {};
    const newAgg = compareNewAgg?.result || {};
    const out: DiffEntry[] = [];
    diffAny(
      {
        consensus_level: oldAgg.consensus_level,
        overall_confidence: oldAgg.overall_confidence,
        num_experts: oldAgg.num_experts,
        final_result: oldAgg.final_result,
      },
      {
        consensus_level: newAgg.consensus_level,
        overall_confidence: newAgg.overall_confidence,
        num_experts: newAgg.num_experts,
        final_result: newAgg.final_result,
      },
      '',
      out,
      5,
      80
    );
    return out;
  }, [compareOldAgg, compareNewAgg]);

  const diffSummarySummary = useMemo(() => {
    const oldAgg = compareOldAgg?.result || {};
    const newAgg = compareNewAgg?.result || {};
    const out: DiffEntry[] = [];
    diffAny(
      {
        consensus_level: oldAgg.consensus_level,
        overall_confidence: oldAgg.overall_confidence,
        num_experts: oldAgg.num_experts,
      },
      {
        consensus_level: newAgg.consensus_level,
        overall_confidence: newAgg.overall_confidence,
        num_experts: newAgg.num_experts,
      },
      '',
      out,
      2,
      80
    );
    return out;
  }, [compareOldAgg, compareNewAgg]);

  const diffSummaryFinal = useMemo(() => {
    const oldAgg = compareOldAgg?.result || {};
    const newAgg = compareNewAgg?.result || {};
    const out: DiffEntry[] = [];
    diffAny(oldAgg.final_result, newAgg.final_result, 'final_result', out, 6, 80);
    return out;
  }, [compareOldAgg, compareNewAgg]);

  const selectedDiffs = useMemo(() => {
    if (diffView === 'summary') return diffSummarySummary;
    if (diffView === 'final_result') return diffSummaryFinal;
    return diffSummaryAll;
  }, [diffView, diffSummaryAll, diffSummarySummary, diffSummaryFinal]);

  const visibleDiffs = useMemo(() => {
    let ds = selectedDiffs.filter((d) => diffKinds[d.kind]);
    if (diffOnlyConfidenceDelta) {
      const threshold = (diffConfidenceThresholdPct || 0) / 100;
      ds = ds.filter((d) => {
        if (!d.path.includes('overall_confidence')) return false;
        const a = typeof d.oldValue === 'number' ? d.oldValue : null;
        const b = typeof d.newValue === 'number' ? d.newValue : null;
        if (a === null || b === null) return false;
        return Math.abs(b - a) >= threshold;
      });
    }
    return ds;
  }, [selectedDiffs, diffKinds, diffOnlyConfidenceDelta, diffConfidenceThresholdPct]);

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      return;
    } catch {
    }

    try {
      const el = document.createElement('textarea');
      el.value = text;
      el.style.position = 'fixed';
      el.style.left = '-9999px';
      document.body.appendChild(el);
      el.select();
      document.execCommand('copy');
      document.body.removeChild(el);
    } catch {
    }
  };

  const loadMe = async () => {
    try {
      const me = await systemAPI.me();
      if (me?.user_id) {
        setUserId(me.user_id);
        return me.user_id as string;
      }
    } catch {
    }
    return userId;
  };

  const loadExperts = async () => {
    try {
      const resp = await systemAPI.experts();
      const names = (resp.experts || []).map((e: any) => e.name).filter(Boolean);
      setExpertOptions(names);
    } catch {
      setExpertOptions([]);
    }
  };

  const loadList = async (nextOffset: number = offset, nextLimit: number = limit, targetUserId: string = userId) => {
    if (!canQuery) return;
    setLoading(true);
    setError(null);
    try {
      const t = computeSinceUntil();
      const resp = await historyAPI.list(targetUserId, q, nextLimit, nextOffset, expertName, consensusLevel, onlyErrors, t.since, t.until, taskType);
      setOffset(nextOffset);
      setLimit(nextLimit);
      setItems(resp.items || []);
    } catch (e: any) {
      setError(e?.message || '加载失败');
    } finally {
      setLoading(false);
    }
  };

  const loadDetail = async (requestId: string) => {
    setLoading(true);
    setError(null);
    try {
      const resp = await historyAPI.detail(userId, requestId);
      setSelected(resp);
      setDetailExpertName('');
      setDetailOnlyErrors(false);
      setCollapsed({});
      setCompareOld(null);
      setCompareNew(null);
    } catch (e: any) {
      setError(e?.message || '加载详情失败');
    } finally {
      setLoading(false);
    }
  };

  const replaySelected = async () => {
    if (!selected?.request?.request_id) return;
    setLoading(true);
    setError(null);
    try {
      const oldSnapshot = selected;
      const payload: any = {};
      if (replayTaskType.trim()) payload.task_type = replayTaskType.trim();
      if (replayExperts.length > 0) payload.expert_names = replayExperts;

      const resp = await historyAPI.replay(userId, selected.request.request_id, payload);
      if (resp?.request_id) {
        const newDetail = await historyAPI.detail(userId, resp.request_id);
        setSelected(newDetail);
        setCompareOld(oldSnapshot);
        setCompareNew(newDetail);
        setDetailExpertName('');
        setDetailOnlyErrors(false);
        setCollapsed({});
      }
    } catch (e: any) {
      setError(e?.message || '重放失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    (async () => {
      const uid = await loadMe();
      await loadList(0, limit, uid);
    })();
    loadExperts();
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">历史 / 复盘</h1>

      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex flex-col md:flex-row gap-3 md:items-center">
          <div className="text-sm text-gray-600">
            user_id: <span className="font-semibold text-gray-800">{userId}</span>
          </div>
          <div className="flex-1" />
          <select
            value={limit}
            onChange={(e) => {
              const v = parseInt(e.target.value, 10);
              setLimit(v);
              setOffset(0);
            }}
            className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
          >
            <option value={20}>20/页</option>
            <option value={50}>50/页</option>
            <option value={100}>100/页</option>
          </select>
          <select
            value={timeRange}
            onChange={(e) => {
              setTimeRange(e.target.value);
              setOffset(0);
            }}
            className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
          >
            <option value="">全部时间</option>
            <option value="24h">最近24h</option>
            <option value="7d">最近7天</option>
            <option value="30d">最近30天</option>
          </select>
          <select
            value={expertName}
            onChange={(e) => setExpertName(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
          >
            <option value="">全部专家</option>
            {expertOptions.map((n) => (
              <option key={n} value={n}>
                {n}
              </option>
            ))}
            <option value="__aggregated__">__aggregated__</option>
          </select>
          <label className="flex items-center gap-2 text-sm text-gray-700">
            <input
              type="checkbox"
              checked={onlyCFO}
              onChange={(e) => {
                const checked = e.target.checked;
                setOnlyCFO(checked);
                setOffset(0);
                if (checked) {
                  setExpertName('CFOExpert');
                  setTaskType('cfo_chat');
                } else {
                  setExpertName('');
                  setTaskType('');
                }
              }}
            />
            仅 CFO
          </label>
          <input
            value={taskType}
            onChange={(e) => setTaskType(e.target.value)}
            placeholder="task_type（可选）"
            className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
            disabled={onlyCFO}
          />
          <select
            value={consensusLevel}
            onChange={(e) => setConsensusLevel(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
          >
            <option value="">全部一致性</option>
            <option value="high">high</option>
            <option value="medium">medium</option>
            <option value="low">low</option>
            <option value="none">none</option>
          </select>
          <label className="flex items-center gap-2 text-sm text-gray-700">
            <input
              type="checkbox"
              checked={onlyErrors}
              onChange={(e) => setOnlyErrors(e.target.checked)}
            />
            仅失败
          </label>
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="关键词（按请求文本搜索）"
            className="flex-1 md:flex-none md:w-96 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
          />
          <button
            onClick={() => loadList(0, limit)}
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? '加载中...' : '查询'}
          </button>
        </div>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 text-red-700 rounded p-4">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-lg font-semibold mb-4">请求列表</h2>
          <div className="space-y-3">
            {items.length === 0 ? (
              <div className="text-sm text-gray-500">暂无记录</div>
            ) : (
              items.map((it) => (
                <div
                  key={it.request_id}
                  className="border rounded p-3 hover:bg-gray-50"
                >
                  <div className="flex justify-between items-start gap-3">
                    <div
                      className="min-w-0 flex-1 cursor-pointer"
                      onClick={() => loadDetail(it.request_id)}
                    >
                      <div className="flex justify-between items-center gap-2">
                        <div className="text-xs text-gray-500">{it.timestamp}</div>
                        <div className="flex items-center gap-2">
                      {it.task_type && (
                        <span className="text-xs px-2 py-1 bg-purple-50 text-purple-700 rounded">
                          {it.task_type}
                        </span>
                      )}
                          {it.consensus_level && (
                            <span className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded">
                              {it.consensus_level}
                            </span>
                          )}
                          {it.overall_confidence != null && (
                            <span className="text-xs px-2 py-1 bg-blue-50 text-blue-700 rounded">
                              {Math.round(it.overall_confidence * 100)}%
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="text-sm font-semibold text-gray-800 truncate">{it.text}</div>
                      <div className="text-xs text-gray-600 truncate">{it.request_id}</div>
                    </div>
                    <div className="flex flex-col gap-2">
                      <button
                        className="px-3 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50"
                        onClick={(e) => {
                          e.stopPropagation();
                          loadDetail(it.request_id);
                        }}
                        disabled={loading}
                      >
                        复盘
                      </button>
                      <button
                        className="px-3 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm hover:bg-gray-200 disabled:opacity-50"
                        onClick={async (e) => {
                          e.stopPropagation();
                          await copyToClipboard(it.request_id);
                        }}
                        disabled={loading}
                      >
                        复制ID
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
          <div className="flex items-center justify-between mt-6">
            <div className="text-xs text-gray-500">
              offset {offset} · limit {limit}
            </div>
            <div className="flex gap-2">
              <button
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm hover:bg-gray-200 disabled:opacity-50"
                disabled={loading || offset === 0}
                onClick={() => loadList(Math.max(0, offset - limit), limit)}
              >
                上一页
              </button>
              <button
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm hover:bg-gray-200 disabled:opacity-50"
                disabled={loading || !hasNextPage}
                onClick={() => loadList(offset + limit, limit)}
              >
                下一页
              </button>
            </div>
          </div>
        </div>

        <div className="lg:col-span-2 bg-white rounded-lg shadow-md p-6">
          <h2 className="text-lg font-semibold mb-4">详情</h2>
          {!selected ? (
            <div className="text-sm text-gray-500">选择一条记录查看</div>
          ) : (
            <div className="space-y-4">
              <div className="border rounded p-4">
                <div className="text-xs text-gray-500 mb-1">Request</div>
                <div className="flex justify-between items-start gap-3">
                  <div className="min-w-0 flex-1">
                    <div className="text-sm font-semibold">{selected.request?.text}</div>
                    <div className="text-xs text-gray-600 mt-2">{selected.request?.request_id}</div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-4">
                      <input
                        value={replayTaskType}
                        onChange={(e) => setReplayTaskType(e.target.value)}
                        placeholder="重放 task_type（可选）"
                        className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                      />
                      <select
                        multiple
                        value={replayExperts}
                        onChange={(e) => {
                          const values = Array.from(e.target.selectedOptions).map((o) => o.value);
                          setReplayExperts(values);
                        }}
                        className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                      >
                        {expertOptions.map((n) => (
                          <option key={n} value={n}>
                            {n}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div className="text-xs text-gray-500 mt-2">
                      多选专家为空表示按默认策略选择；可用 Cmd/Ctrl 多选
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      className="px-3 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50"
                      onClick={replaySelected}
                      disabled={loading}
                    >
                      重放
                    </button>
                    <button
                      className="px-3 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm hover:bg-gray-200"
                      onClick={async () => {
                        const filename = `history_${selected.request?.request_id || 'request'}.json`;
                        const payload = JSON.stringify(selected, null, 2);
                        const blob = new Blob([payload], { type: 'application/json;charset=utf-8' });
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = filename;
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        URL.revokeObjectURL(url);
                      }}
                    >
                      下载 JSON
                    </button>
                  </div>
                </div>
              </div>

              {compareOld && compareNew && (
                <div className="border rounded p-4">
                  <div className="flex justify-between items-center mb-3">
                    <div className="text-xs text-gray-500">Compare</div>
                    <button
                      className="px-3 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm hover:bg-gray-200"
                      onClick={() => {
                        setCompareOld(null);
                        setCompareNew(null);
                      }}
                    >
                      退出对比
                    </button>
                  </div>
                  <div className="border rounded p-3 mb-4">
                    <div className="flex flex-col md:flex-row gap-3 md:items-center mb-2">
                      <div className="text-xs text-gray-500">Changes</div>
                      <div className="flex-1" />
                      <select
                        value={diffView}
                        onChange={(e) => setDiffView(e.target.value as any)}
                        className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                      >
                        <option value="all">全部</option>
                        <option value="summary">仅摘要字段</option>
                        <option value="final_result">仅 final_result</option>
                      </select>
                      <div className="hidden md:flex items-center gap-2">
                        {(['added', 'removed', 'changed', 'type_changed'] as DiffKind[]).map((k) => (
                          <label key={k} className="flex items-center gap-1 text-xs text-gray-700">
                            <input
                              type="checkbox"
                              checked={diffKinds[k]}
                              onChange={(e) => setDiffKinds((prev) => ({ ...prev, [k]: e.target.checked }))}
                            />
                            {k}
                          </label>
                        ))}
                      </div>
                      <label className="flex items-center gap-2 text-sm text-gray-700">
                        <input
                          type="checkbox"
                          checked={diffOnlyConfidenceDelta}
                          onChange={(e) => setDiffOnlyConfidenceDelta(e.target.checked)}
                        />
                        仅置信度变化
                      </label>
                      <select
                        value={diffConfidenceThresholdPct}
                        onChange={(e) => setDiffConfidenceThresholdPct(parseInt(e.target.value, 10))}
                        className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                        disabled={!diffOnlyConfidenceDelta}
                      >
                        <option value={5}>&gt;=5%</option>
                        <option value={10}>&gt;=10%</option>
                        <option value={20}>&gt;=20%</option>
                        <option value={30}>&gt;=30%</option>
                      </select>
                      <button
                        className="px-3 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm hover:bg-gray-200"
                        onClick={async () => {
                          await copyToClipboard(JSON.stringify(visibleDiffs, null, 2));
                        }}
                      >
                        复制差异JSON
                      </button>
                      <button
                        className="px-3 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm hover:bg-gray-200"
                        onClick={async () => {
                          await copyToClipboard(buildDiffMarkdown(visibleDiffs));
                        }}
                      >
                        复制差异MD
                      </button>
                    </div>
                    {visibleDiffs.length === 0 ? (
                      <div className="text-sm text-gray-600">无差异</div>
                    ) : (
                      <div className="space-y-2">
                        {visibleDiffs.slice(0, 30).map((d) => (
                          <div key={d.path + d.kind} className="text-xs border rounded p-2 bg-gray-50">
                            <div className="flex justify-between items-center gap-2">
                              <div className="font-semibold text-gray-800 truncate">{d.path || '(root)'}</div>
                              <span className="px-2 py-1 rounded bg-white text-gray-700 border">{d.kind}</span>
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-2">
                              <div className="text-gray-600">
                                old: <span className="text-gray-800">{toPreview(d.oldValue)}</span>
                              </div>
                              <div className="text-gray-600">
                                new: <span className="text-gray-800">{toPreview(d.newValue)}</span>
                              </div>
                            </div>
                          </div>
                        ))}
                        {visibleDiffs.length > 30 && (
                          <div className="text-xs text-gray-500">仅展示前 30 条差异（共 {visibleDiffs.length} 条）</div>
                        )}
                      </div>
                    )}
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="border rounded p-3">
                      <div className="text-xs text-gray-500 mb-2">Old</div>
                      <div className="text-xs text-gray-700">
                        consensus: {compareOldAgg?.result?.consensus_level ?? '-'} · confidence:{' '}
                        {compareOldAgg?.result?.overall_confidence != null
                          ? `${Math.round(compareOldAgg.result.overall_confidence * 100)}%`
                          : '-'}
                      </div>
                      <pre className="text-xs bg-gray-50 rounded p-3 mt-2 overflow-auto">
{JSON.stringify(compareOldAgg?.result?.final_result, null, 2)}
                      </pre>
                    </div>
                    <div className="border rounded p-3">
                      <div className="text-xs text-gray-500 mb-2">New</div>
                      <div className="text-xs text-gray-700">
                        consensus: {compareNewAgg?.result?.consensus_level ?? '-'} · confidence:{' '}
                        {compareNewAgg?.result?.overall_confidence != null
                          ? `${Math.round(compareNewAgg.result.overall_confidence * 100)}%`
                          : '-'}
                      </div>
                      <pre className="text-xs bg-gray-50 rounded p-3 mt-2 overflow-auto">
{JSON.stringify(compareNewAgg?.result?.final_result, null, 2)}
                      </pre>
                    </div>
                  </div>
                </div>
              )}

              {aggregated && (
                <div className="border rounded p-4">
                  <div className="text-xs text-gray-500 mb-3">Aggregated</div>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    <div className="bg-gray-50 rounded p-3">
                      <div className="text-xs text-gray-500">consensus</div>
                      <div className="font-semibold text-gray-800">{aggregated.result?.consensus_level ?? '-'}</div>
                    </div>
                    <div className="bg-gray-50 rounded p-3">
                      <div className="text-xs text-gray-500">overall_confidence</div>
                      <div className="font-semibold text-gray-800">
                        {aggregated.result?.overall_confidence != null
                          ? `${Math.round(aggregated.result.overall_confidence * 100)}%`
                          : '-'}
                      </div>
                    </div>
                    <div className="bg-gray-50 rounded p-3">
                      <div className="text-xs text-gray-500">experts</div>
                      <div className="font-semibold text-gray-800">{aggregated.result?.num_experts ?? '-'}</div>
                    </div>
                  </div>
                  <pre className="text-xs bg-gray-50 rounded p-3 mt-3 overflow-auto">
{JSON.stringify(aggregated.result?.final_result, null, 2)}
                  </pre>
                </div>
              )}

              <div className="border rounded p-4">
                <div className="text-xs text-gray-500 mb-3">Results</div>
                <div className="flex flex-col md:flex-row gap-3 md:items-center mb-4">
                  <select
                    value={detailExpertName}
                    onChange={(e) => setDetailExpertName(e.target.value)}
                    className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-600"
                  >
                    <option value="">全部专家</option>
                    {expertResults.map((r: any) => r.expert_name).filter((v: any, idx: number, arr: any[]) => arr.indexOf(v) === idx).map((n: string) => (
                      <option key={n} value={n}>
                        {n}
                      </option>
                    ))}
                  </select>
                  <label className="flex items-center gap-2 text-sm text-gray-700">
                    <input
                      type="checkbox"
                      checked={detailOnlyErrors}
                      onChange={(e) => setDetailOnlyErrors(e.target.checked)}
                    />
                    仅错误
                  </label>
                  <div className="flex-1" />
                  <button
                    className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm hover:bg-gray-200"
                    onClick={() => {
                      const next: Record<string, boolean> = {};
                      for (const r of filteredDetailResults) next[r.result_id] = true;
                      setCollapsed(next);
                    }}
                  >
                    全部收起
                  </button>
                  <button
                    className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm hover:bg-gray-200"
                    onClick={() => setCollapsed({})}
                  >
                    全部展开
                  </button>
                </div>
                <div className="space-y-3">
                  {filteredDetailResults.map((r: any) => (
                    <div key={r.result_id} className="border rounded p-3">
                      <div className="flex justify-between items-center">
                        <div className="font-semibold text-gray-800">{r.expert_name}</div>
                        <div className="flex items-center gap-3">
                          <div className="text-xs text-gray-500">{r.duration_ms?.toFixed ? `${r.duration_ms.toFixed(0)}ms` : ''}</div>
                          <button
                            className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                            onClick={() => setCollapsed((prev) => ({ ...prev, [r.result_id]: !prev[r.result_id] }))}
                          >
                            {collapsed[r.result_id] ? '展开' : '收起'}
                          </button>
                        </div>
                      </div>
                      {r.error && <div className="text-sm text-red-600 mt-2">{r.error}</div>}
                      {!collapsed[r.result_id] && (
                        <pre className="text-xs bg-gray-50 rounded p-3 mt-2 overflow-auto">
{JSON.stringify(r.result, null, 2)}
                        </pre>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default History;
