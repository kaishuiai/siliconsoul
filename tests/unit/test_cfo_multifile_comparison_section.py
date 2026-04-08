from src.cfo.subagents.section_orchestrator import CFOSectionOrchestrator


def test_multifile_comparison_section_in_report():
    orch = CFOSectionOrchestrator()
    extra_params = {
        "file_paths": ["/tmp/ACME_2024Q4.xlsx", "/tmp/ACME_2025Q1.xlsx"],
        "per_file_indicators": [
            {
                "file_path": "/tmp/ACME_2024Q4.xlsx",
                "indicators": {"gross_margin": 0.40, "net_margin": 0.10, "roe": 0.08, "debt_to_assets": 0.50},
            },
            {
                "file_path": "/tmp/ACME_2025Q1.xlsx",
                "indicators": {"gross_margin": 0.42, "net_margin": 0.11, "roe": 0.085, "debt_to_assets": 0.52},
            },
        ],
    }
    sections = orch.build_sections(
        query="compare",
        task_type="financial_analysis",
        intent="indicator_calculation",
        indicators={"gross_margin": 0.42, "net_margin": 0.11, "roe": 0.085, "debt_to_assets": 0.52},
        snippets=[],
        has_parsed_data=True,
        extra_params=extra_params,
    )
    report = orch.assemble_report(
        query="compare",
        intent="indicator_calculation",
        task_type="financial_analysis",
        indicators={"gross_margin": 0.42, "net_margin": 0.11, "roe": 0.085, "debt_to_assets": 0.52},
        sections=sections,
        has_parsed_data=True,
    )
    assert "多文件对比" in report
    assert "| 期间 | 文件 |" in report
    assert "2024Q4" in report
    assert "2025Q1" in report


def test_multifile_yoy_delta():
    orch = CFOSectionOrchestrator()
    extra_params = {
        "file_paths": ["/tmp/ACME_2024Q1.xlsx", "/tmp/ACME_2025Q1.xlsx"],
        "per_file_indicators": [
            {
                "file_path": "/tmp/ACME_2024Q1.xlsx",
                "indicators": {"gross_margin": 0.40, "net_margin": 0.10, "roe": 0.08, "debt_to_assets": 0.50},
            },
            {
                "file_path": "/tmp/ACME_2025Q1.xlsx",
                "indicators": {"gross_margin": 0.42, "net_margin": 0.11, "roe": 0.085, "debt_to_assets": 0.52},
            },
        ],
    }
    sec = orch.build_sections(
        query="compare",
        task_type="financial_analysis",
        intent="indicator_calculation",
        indicators={"gross_margin": 0.42, "net_margin": 0.11, "roe": 0.085, "debt_to_assets": 0.52},
        snippets=[],
        has_parsed_data=True,
        extra_params=extra_params,
    )["multi_file_comparison"]
    md = str(sec.get("markdown") or "")
    assert "同比" in md
    assert "2024Q1" in md and "2025Q1" in md

