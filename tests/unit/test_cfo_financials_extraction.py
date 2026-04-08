import pytest

from src.cfo.tools import compute_financial_indicators, extract_financials


def test_extract_financials_from_tables_with_unit():
    parsed = {
        "text": "合并利润表（单位：万元）",
        "tables": [
            [
                {"科目": "营业收入", "本期": "12,000"},
                {"科目": "营业成本", "本期": "7,200"},
                {"科目": "净利润", "本期": "1,800"},
            ],
            [
                {"科目": "资产总计", "期末": "50,000"},
                {"科目": "负债合计", "期末": "30,000"},
                {"科目": "所有者权益合计", "期末": "20,000"},
                {"科目": "存货", "期末": "5,000"},
            ],
        ],
    }

    out = extract_financials(parsed)
    assert out["is_mock_data"] is False
    assert out["unit"] == "万元"
    assert out["unit_multiplier"] == 10000.0
    values = out["values"]
    assert values["revenue"] == 12000.0
    assert values["cost"] == 7200.0
    assert values["net_income"] == 1800.0
    assert values["total_assets"] == 50000.0
    assert values["total_liabilities"] == 30000.0
    assert values["total_equity"] == 20000.0
    assert values["inventory"] == 5000.0


def test_compute_financial_indicators_scales_values_and_keeps_ratios():
    parsed = {
        "text": "合并利润表（单位：万元）",
        "tables": [
            [
                {"科目": "营业收入", "本期": "12,000"},
                {"科目": "营业成本", "本期": "7,200"},
                {"科目": "净利润", "本期": "1,800"},
            ],
            [
                {"科目": "资产总计", "期末": "50,000"},
                {"科目": "负债合计", "期末": "30,000"},
                {"科目": "所有者权益合计", "期末": "20,000"},
                {"科目": "存货", "期末": "5,000"},
            ],
        ],
    }

    out = compute_financial_indicators(parsed)
    assert out["is_mock_data"] is False
    assert out["unit_multiplier"] == 10000.0
    assert out["gross_margin"] == 0.4
    assert out["roe"] == 0.09
    values = out["values"]
    assert values["revenue"] == 12000.0 * 10000.0
    assert values["total_assets"] == 50000.0 * 10000.0

