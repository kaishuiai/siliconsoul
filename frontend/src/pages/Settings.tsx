import React, { useEffect, useState } from 'react';
import { systemAPI } from '../services/api';

const PROVIDERS = [
  { value: 'openai_compatible', label: 'OpenAI兼容' },
  { value: 'deepseek', label: 'DeepSeek' },
  { value: 'zenmux', label: 'Zenmux（OpenAI兼容）' },
  { value: 'custom', label: '自定义兼容服务' },
];

const Settings: React.FC = () => {
  const [provider, setProvider] = useState('openai_compatible');
  const [apiBase, setApiBase] = useState('');
  const [model, setModel] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [keyHint, setKeyHint] = useState('');
  const [cfoLLM, setCfoLLM] = useState(false);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState('');
  const [err, setErr] = useState('');
  const [legacyMode, setLegacyMode] = useState(false);

  useEffect(() => {
    (async () => {
      try {
        const cfg = await systemAPI.getConfig();
        try {
          const llm = await systemAPI.getLLMSettings();
          setProvider(llm?.provider || cfg?.llm?.provider || 'openai_compatible');
          setApiBase(llm?.api_base || cfg?.llm?.api_base || '');
          setModel(llm?.model || cfg?.llm?.model || '');
          setKeyHint(llm?.has_api_key ? `已配置密钥（后4位：${llm?.api_key_tail || '****'}）` : '未配置密钥');
          setLegacyMode(false);
        } catch (e: any) {
          const status = e?.response?.status;
          if (status === 404) {
            setLegacyMode(true);
            setProvider(cfg?.llm?.provider || 'openai_compatible');
            setApiBase(cfg?.llm?.api_base || '');
            setModel(cfg?.llm?.model || '');
            setKeyHint('当前后端未启用密钥设置接口（可先保存基础配置）');
          } else {
            throw e;
          }
        }
        setCfoLLM(Boolean(cfg?.cfo?.enable_llm));
      } catch (e: any) {
        setErr(e?.message || '加载设置失败');
      }
    })();
  }, []);

  const save = async () => {
    setSaving(true);
    setErr('');
    setMsg('');
    try {
      if (!legacyMode) {
        await systemAPI.setLLMSettings({
          provider,
          api_base: apiBase || undefined,
          model: model || undefined,
          api_key: apiKey || undefined,
        });
      } else {
        await systemAPI.setConfig('llm.provider', provider === 'zenmux' || provider === 'custom' ? 'openai_compatible' : provider);
        await systemAPI.setConfig('llm.api_base', apiBase || null);
        await systemAPI.setConfig('llm.model', model || null);
      }
      await systemAPI.setConfig('cfo.enable_llm', cfoLLM);
      setApiKey('');
      if (!legacyMode) {
        const current = await systemAPI.getLLMSettings();
        setKeyHint(current?.has_api_key ? `已配置密钥（后4位：${current?.api_key_tail || '****'}）` : '未配置密钥');
      } else {
        setKeyHint('基础配置已保存；密钥请通过环境变量（如 .env.local）配置');
      }
      setMsg(legacyMode ? '基础设置已保存（后端较旧，密钥接口未启用）' : '设置已保存（仅本地运行时生效，不写入 Git）');
    } catch (e: any) {
      setErr(e?.message || '保存失败');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="p-6 max-w-4xl">
      <h1 className="text-2xl font-bold mb-2">设置</h1>
      <p className="text-sm text-gray-600 mb-6">配置常用 LLM API 或自定义兼容服务（如 Zenmux）。</p>
      {legacyMode && (
        <div className="mb-4 text-sm text-amber-700 bg-amber-50 border border-amber-200 rounded px-3 py-2">
          检测到后端未启用 /api/llm/settings（404）。已自动切换兼容模式：可保存基础配置，密钥请用环境变量配置并重启后端。
        </div>
      )}

      <div className="bg-white rounded-lg shadow-md p-6 space-y-4">
        <div>
          <label className="block text-sm text-gray-700 mb-2">服务类型</label>
          <select value={provider} onChange={(e) => setProvider(e.target.value)} className="w-full border rounded px-3 py-2">
            {PROVIDERS.map((p) => (
              <option key={p.value} value={p.value}>{p.label}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm text-gray-700 mb-2">API Base（可选）</label>
          <input value={apiBase} onChange={(e) => setApiBase(e.target.value)} className="w-full border rounded px-3 py-2" placeholder="如 https://your-gateway/v1" />
        </div>
        <div>
          <label className="block text-sm text-gray-700 mb-2">模型名（可选）</label>
          <input value={model} onChange={(e) => setModel(e.target.value)} className="w-full border rounded px-3 py-2" placeholder="如 gpt-4o-mini / deepseek-chat" />
        </div>
        <div>
          <label className="block text-sm text-gray-700 mb-2">API Key（输入后更新）</label>
          <input type="password" value={apiKey} onChange={(e) => setApiKey(e.target.value)} className="w-full border rounded px-3 py-2" placeholder="留空则不覆盖当前密钥" />
          <div className="text-xs text-gray-500 mt-1">{keyHint}</div>
        </div>
        <div className="flex items-center gap-2">
          <input id="cfo-llm" type="checkbox" checked={cfoLLM} onChange={(e) => setCfoLLM(e.target.checked)} />
          <label htmlFor="cfo-llm" className="text-sm text-gray-700">启用 CFO 流程 LLM</label>
        </div>
        {err && <div className="text-sm text-red-600">{err}</div>}
        {msg && <div className="text-sm text-green-600">{msg}</div>}
        <div className="pt-2">
          <button onClick={save} disabled={saving} className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50">
            {saving ? '保存中...' : '保存设置'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Settings;
