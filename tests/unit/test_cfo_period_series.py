from src.cfo.tools import compute_period_changes, extract_financials_series


def test_extract_financials_series_from_documents_and_period_inference():
    parsed_data = {
        "documents": [
            {
                "file_path": "/tmp/ACME_2023Q4.xlsx",
                "parsed": {
                    "text": "合并利润表（单位：万元）",
                    "tables": [[{"科目": "营业收入", "本期": "10,000"}, {"科目": "营业成本", "本期": "6,000"}, {"科目": "净利润", "本期": "1,200"}]],
                },
            },
            {
                "file_path": "/tmp/ACME_2024Q1.xlsx",
                "parsed": {
                    "text": "合并利润表（单位：万元）",
                    "tables": [[{"科目": "营业收入", "本期": "12,000"}, {"科目": "营业成本", "本期": "7,200"}, {"科目": "净利润", "本期": "1,800"}]],
                },
            },
        ]
    }

    out = extract_financials_series(parsed_data)
    series = out["series"]
    assert len(series) == 2
    assert series[0]["period"] == "2024Q1"
    assert series[1]["period"] == "2023Q4"


def test_compute_period_changes_rate():
    series = [
        {"period": "2024Q1", "period_sort": [2024, 1, 0], "values": {"revenue": 120.0, "net_income": 18.0}},
        {"period": "2023Q4", "period_sort": [2023, 4, 0], "values": {"revenue": 100.0, "net_income": 10.0}},
    ]
    out = compute_period_changes(series)
    assert out["latest"]["period"] == "2024Q1"
    assert out["previous"]["period"] == "2023Q4"
    assert abs(out["changes"]["revenue"]["change_rate"] - 0.2) < 1e-9
    assert abs(out["changes"]["net_income"]["change_rate"] - 0.8) < 1e-9

