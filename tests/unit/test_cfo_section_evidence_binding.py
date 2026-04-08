from src.cfo.subagents.section_orchestrator import CFOSectionOrchestrator


def test_assemble_report_includes_section_sources_and_overview():
    orch = CFOSectionOrchestrator()

    sections = {
        "driver_decomposition": {"markdown": "### 驱动拆解\n内容"},
        "risk_diagnosis": {"markdown": "### 风险诊断\n内容"},
    }
    snippets_by_purpose = {
        "分部/产品收入": [{"snippet": "收入证据", "file_path": "/tmp/rev.xlsx"}],
        "成本明细": [{"snippet": "成本证据", "file_path": "/tmp/cost.xlsx"}],
    }

    report = orch.assemble_report(
        query="test",
        intent="financial_analysis",
        task_type="cfo_chat",
        indicators={},
        sections=sections,
        has_parsed_data=True,
        snippets_by_purpose=snippets_by_purpose,
        business_context={"include_allocations": False},
    )
    assert "### 章节引用概览" in report
    assert "#### 本节依据" in report
    assert "分部/产品收入（rev.xlsx）" in report
