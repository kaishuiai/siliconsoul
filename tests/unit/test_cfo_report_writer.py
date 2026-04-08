from src.cfo.subagents.report_writer import CFOReportWriter


def test_cfo_report_writer_outputs_sections():
    writer = CFOReportWriter()
    report = writer.write(
        intent="risk_diagnosis",
        query="测试",
        indicators={"gross_margin": 0.4, "net_margin": 0.1, "roe": 0.05, "debt_to_assets": 0.6},
        snippets=[{"snippet": "证据片段 1"}, {"snippet": "证据片段 2"}],
        has_parsed_data=True,
    )
    assert "CFO 财务分析报告" in report
    assert "风险诊断分析" in report
    assert "文档依据摘录" in report
