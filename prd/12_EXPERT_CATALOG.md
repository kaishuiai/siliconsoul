# Expert 目录与规格

本文件列出仓库内全部 Expert，并统一说明：能力范围、支持任务、输入依赖与输出字段口径。

## 统一规范

- 输入：ExpertRequest（text/user_id/context/task_type/extra_params）
- 输出：ExpertResult（expert_name/result/confidence/metadata/timestamp_start/timestamp_end/error）

## 专家清单

### 1) StockAnalysisExpert

- 文件：[stock_analysis_expert.py](file:///Users/justinking/02%20Areas%20(%E9%95%BF%E6%9C%9F%E8%B4%A3%E4%BB%BB%E9%A2%86%E5%9F%9F)/siliconsoul/siliconsoul/src/experts/stock_analysis_expert.py)
- 支持任务：stock_analysis、technical_analysis
- 主要输入（extra_params）：
  - symbol（默认 600000.SH）
  - period_days（默认 60）
  - indicators（默认 MA/RSI/MACD/Bollinger）
- 外部依赖：
  - TushareProvider（A 股）
  - 可选 akshare、yfinance（数据源 fallback）
- 输出（result）建议字段：
  - symbol、current_price、date、indicators、signal、confidence、data_source、recommendation
- 风险：
  - 外部数据源不稳定/限流/缺 key
  - 指标计算需明确窗口与参数口径

### 2) KnowledgeExpert

- 文件：[knowledge_expert.py](file:///Users/justinking/02%20Areas%20(%E9%95%BF%E6%9C%9F%E8%B4%A3%E4%BB%BB%E9%A2%86%E5%9F%9F)/siliconsoul/siliconsoul/src/experts/knowledge_expert.py)
- 支持任务：knowledge_query、information_retrieval、knowledge_retrieval、semantic_search、qa
- 主要输入（extra_params）：
  - knowledge_sources（默认 local_docs/analysis_cache/user_history）
  - top_k（默认 5）
  - min_confidence（默认 0）
- 外部依赖：无外部 API（当前为内置缓存模拟）
- 输出（result）字段：
  - query
  - knowledge_items[]（source/title/content/relevance_score/confidence）
  - summary
  - recommendations[]
- 风险：
  - 若引入真实向量库/文档检索，需要落地数据来源与索引策略

### 3) DialogExpert

- 文件：[dialog_expert.py](file:///Users/justinking/02%20Areas%20(%E9%95%BF%E6%9C%9F%E8%B4%A3%E4%BB%BB%E9%A2%86%E5%9F%9F)/siliconsoul/siliconsoul/src/experts/dialog_expert.py)
- 支持任务：dialog、intent_classification、entity_extraction
- 主要输入：
  - text（或 extra_params.text）
  - user_id（用于会话历史）
- 外部依赖：
  - DeepSeek Chat Completions（DEEPSEEK_API_KEY）
  - OpenAI 兼容（LLM_API_BASE + OPENAI_API_KEY）
- 输出（result）字段：
  - user_input、response、intent、intent_confidence、entities、conversation_id
- 风险：
  - key 缺失/网络错误
  - 输出可解释性与一致性，需要明确 prompt/版本

### 4) CFOExpert

- 文件：[cfo_expert.py](file:///Users/justinking/02%20Areas%20(%E9%95%BF%E6%9C%9F%E8%B4%A3%E4%BB%BB%E9%A2%86%E5%9F%9F)/siliconsoul/siliconsoul/src/experts/cfo_expert.py)
- 支持任务：
  - financial_analysis、document_parsing、cfo_chat、risk_diagnosis、trend_prediction
  - cfo_finance_computation（财务计算）
  - cfo_finance_text_analysis（财报文本/表格解读与抽取）
  - cfo_finance_knowledge_qa（资料检索问答，带引用）
  - cfo_finance_consulting（CFO 咨询）
- 主要输入（extra_params）：
  - file_path：PDF/Excel 绝对路径（可选，用于解析与证据检索）
  - file_paths：PDF/Excel 绝对路径列表（可选；优先于 file_path，用于批量解析与汇总分析）
  - financials：标准化财务字段（可选，优先于解析结果；如 revenue/cost/net_income/total_assets/total_liabilities/total_equity/inventory）
  - finance_calc：财务计算指令（可选，结构：{tool,args}；tool 例如 finance.irr/finance.npv/finance.cagr/finance.pv/finance.fv/finance.amortization/finance.break_even/math.solve_linear/math.solve_quadratic）
- 输出（result）字段：
  - intent：内部意图（indicator_calculation / risk_diagnosis / trend_prediction / finance_*）
  - analysis_report：Markdown 报告（若为专项能力任务，直接输出专项结果）
  - indicators：指标与校验（含 is_mock_data/values/validations）
  - per_file_indicators：当传入 file_paths 时，按文件拆分的指标列表（file_path/indicators）
  - financials_series：多文件/多期抽取的标准化财务序列（period/values/unit/is_mock_data 等）
  - period_changes：最近两期（latest vs previous）的关键指标变化（同时提供 change_rate；对毛利率/净利率/ROE/资产负债率提供 delta_pp）
  - snippets：证据片段（evidence_id/snippet/score/...）
  - sections：基础报告分节（executive_summary/key_metrics/risk_diagnosis/outlook/recommendations/qna）
  - sections.driver_decomposition：驱动拆解（DuPont + 利润率桥；在 financials_series >=2 时启用）
  - file_paths：若传入批量文件，则回显解析使用的文件列表
  - capability_output：专项能力输出（capability/answer_markdown/structured/confidence/needs_followup/followup_question）
  - consulting：咨询输出（同上，取决于配置是否启用）
- 风险：
  - 若未提供报表或标准化 financials，指标可能进入演示口径（is_mock_data=true）
  - 专项能力若启用 LLM，需要明确合规边界与引用约束（禁止编造）

### 5) DecisionExpert

- 文件：[decision_expert.py](file:///Users/justinking/02%20Areas%20(%E9%95%BF%E6%9C%9F%E8%B4%A3%E4%BB%BB%E9%A2%86%E5%9F%9F)/siliconsoul/siliconsoul/src/experts/decision_expert.py)
- 支持任务：decision_support、risk_assessment、decision_making、result_aggregation、recommendation
- 主要输入（extra_params）：
  - expert_results（列表，元素需含 confidence 等键）
- 输出（result）字段：
  - aggregated_results、decision、confidence、reasoning、risk_level
- 风险：
  - 若上游 expert_results 结构漂移，聚合逻辑会失真

### 6) ReflectionExpert

- 文件：[reflection_expert.py](file:///Users/justinking/02%20Areas%20(%E9%95%BF%E6%9C%9F%E8%B4%A3%E4%BB%BB%E9%A2%86%E5%9F%9F)/siliconsoul/siliconsoul/src/experts/reflection_expert.py)
- 支持任务：decision_review、lesson_extraction、reflection、quality_assessment、continuous_learning
- 主要输入（extra_params）：
  - decision（上游决策对象）
- 输出（result）字段：
  - quality_score、assessment、improvement_suggestions、confidence_level

### 7) ExecutionExpert

- 文件：[execution_expert.py](file:///Users/justinking/02%20Areas%20(%E9%95%BF%E6%9C%9F%E8%B4%A3%E4%BB%BB%E9%A2%86%E5%9F%9F)/siliconsoul/siliconsoul/src/experts/execution_expert.py)
- 支持任务：task_execution、progress_tracking、trade_execution、position_tracking、result_verification
- 外部依赖：无真实交易 API（当前为模拟）
- 输出（result）字段：
  - execution_status、order_id、executed_price、quantity、timestamp、commission

### 8) MLExpert

- 文件：[ml_expert.py](file:///Users/justinking/02%20Areas%20(%E9%95%BF%E6%9C%9F%E8%B4%A3%E4%BB%BB%E9%A2%86%E5%9F%9F)/siliconsoul/siliconsoul/src/experts/ml_expert.py)
- 支持任务：price_prediction、anomaly_detection、risk_scoring、sentiment_analysis
- 主要输入（extra_params）：
  - task（默认 price_prediction）
  - prices（至少 10 个价格点）
- 外部依赖：numpy（本地计算）
- 输出（result）字段：按 task 不同返回不同字段（预测/异常/风险/情感）

### 9) DemoExpert1/2/3

- 文件：
  - [demo_expert_1.py](file:///Users/justinking/02%20Areas%20(%E9%95%BF%E6%9C%9F%E8%B4%A3%E4%BB%BB%E9%A2%86%E5%9F%9F)/siliconsoul/siliconsoul/src/experts/demo_expert_1.py)
  - [demo_expert_2.py](file:///Users/justinking/02%20Areas%20(%E9%95%BF%E6%9C%9F%E8%B4%A3%E4%BB%BB%E9%A2%86%E5%9F%9F)/siliconsoul/siliconsoul/src/experts/demo_expert_2.py)
  - [demo_expert_3.py](file:///Users/justinking/02%20Areas%20(%E9%95%BF%E6%9C%9F%E8%B4%A3%E4%BB%BB%E9%A2%86%E5%9F%9F)/siliconsoul/siliconsoul/src/experts/demo_expert_3.py)
- 用途：演示/测试专家接口与并发执行，不依赖外部数据源
