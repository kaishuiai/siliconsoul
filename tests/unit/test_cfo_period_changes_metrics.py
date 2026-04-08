from src.cfo import tools as cfo_tools


def test_compute_period_changes_supports_derived_metrics():
    series = [
        {
            "period": "2025Q1",
            "period_sort": [2025, 1, 0],
            "values": {
                "revenue": 12000.0,
                "cost": 7200.0,
                "net_income": 1800.0,
                "total_assets": 54000.0,
                "total_liabilities": 32000.0,
                "total_equity": 22000.0,
            },
        },
        {
            "period": "2024Q4",
            "period_sort": [2024, 4, 0],
            "values": {
                "revenue": 10000.0,
                "cost": 6000.0,
                "net_income": 1500.0,
                "total_assets": 50000.0,
                "total_liabilities": 30000.0,
                "total_equity": 20000.0,
            },
        },
    ]
    out = cfo_tools.compute_period_changes(series=series)
    assert isinstance(out, dict)
    changes = out.get("changes") or {}
    assert "revenue" in changes
    assert "gross_margin" in changes
    assert "net_margin" in changes
    assert "asset_turnover" in changes
    assert "equity_multiplier" in changes
    assert "roe" in changes
    assert "debt_to_assets" in changes
