# CFO 场景：多文档上传与财务分析

## 界面入口（当前已有）

本仓库提供 Streamlit CFO 页面，用于一次上传多个财务/业务材料并对话式提出分析要求：

```bash
streamlit run frontend/cfo_streamlit_app.py
```

Docker Compose（推荐）：

```bash
docker compose up -d siliconsoul siliconsoul-web siliconsoul-cfo
```

环境变量：

- CFO_API_URL：CFO 页面请求后端 API（默认 http://localhost:8000/api；compose 内为 http://siliconsoul:8000/api）

## 子业务/子产品模板

页面提供“子业务/子产品分析模板”表单：

- 结构化填写业务边界、期间、口径、分摊规则、经营指标
- 一键生成“分析指令”，可编辑后发送
- 支持 Presets（保存/加载/删除/导入/导出），按 user_id 落盘到 data/cfo_presets/

## 文件用途标签

上传到服务器后，CFO 页面允许对每个文件选择用途标签（例如：财报/分部产品收入/成本明细/费用分摊/经营指标/合同定价）。

- 用途标签会随分析请求一起发送，用于证据摘录与报告组织
- 输出中会提供按用途分组的证据摘录 snippets_by_purpose

## 支持的文件类型

- PDF：.pdf
- Excel：.xlsx / .xls
- PowerPoint：.pptx（.ppt 为旧格式，建议转换为 .pptx）
- Word：.docx（.doc 为旧格式，建议转换为 .docx）

## 鉴权（可选）

当后端配置 auth.enabled=true 且配置了 auth.tokens（或环境变量 SILICONSOUL_API_TOKENS）时，CFO 页面需要在侧边栏输入 Token 才能使用，并将 token 映射的 user_id 用于 Presets 落盘隔离。

## 历史/复盘联动

CFO 页面通过后端 HTTP API（/api/uploads + /api/process）执行分析，因此每次分析都会自动落盘并可在主站“历史/复盘”中按 user_id 查询与回放。

建议在主站“历史/复盘”里使用：

- 仅 CFO：快速过滤 CFOExpert 的记录
- task_type=cfo_chat：仅显示 CFO 对话分析

## 材料缺口（needs_structured）

CFO 输出会返回结构化的材料缺口：

- needs_structured: [{category, priority, text, why, example}]
- needs: [text...]（兼容字段）

CFO 页面会把 needs_structured 渲染为 checklist，便于逐项补齐材料。

## 报告导出

CFO 页面支持将本次分析结果导出为 Markdown 报告（包含按用途的材料依据与 needs checklist）。

## 使用建议（子业务/子产品分析）

当你要分析某个子业务/子产品时，建议在问题中明确：

- 子业务/子产品边界（期间、口径、合并范围、是否含分摊）
- 收入拆分（量×价、渠道/地区/客户）
- 成本结构与毛利（直接成本、单位成本、关键成本项）
- 费用分摊规则（销售/研发/管理）
- 现金流与营运资本（回款/应收/存货/预付）
