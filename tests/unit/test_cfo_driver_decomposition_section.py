from src.cfo.subagents.section_orchestrator import CFOSectionOrchestrator


def test_driver_decomposition_section_renders_when_series_present():
    orch = CFOSectionOrchestrator()
    series = [
        {
            "period": "2025Q1",
            "values": {
                "revenue": 12000.0,
                "cost": 7200.0,
                "net_income": 1800.0,
                "total_assets": 54000.0,
                "total_liabilities": 32000.0,
                "total_equity": 22000.0,
                "selling_expense": 300.0,
                "admin_expense": 400.0,
                "rd_expense": 500.0,
                "finance_expense": 120.0,
                "tax_expense": 200.0,
            },
        },
        {
            "period": "2024Q4",
            "values": {
                "revenue": 10000.0,
                "cost": 6000.0,
                "net_income": 1500.0,
                "total_assets": 50000.0,
                "total_liabilities": 30000.0,
                "total_equity": 20000.0,
                "selling_expense": 260.0,
                "admin_expense": 380.0,
                "rd_expense": 420.0,
                "finance_expense": 100.0,
                "tax_expense": 180.0,
            },
        },
    ]
    sec = orch.build_sections(
        query="decompose",
        task_type="financial_analysis",
        intent="indicator_calculation",
        indicators={"gross_margin": 0.4, "net_margin": 0.1, "roe": 0.08, "debt_to_assets": 0.6},
        snippets=[],
        has_parsed_data=True,
        extra_params={"financials_series": series},
    ).get("driver_decomposition")
    md = str((sec or {}).get("markdown") or "")
    assert "驱动拆解" in md
    assert "DuPont" in md
    assert "费用率" in md

