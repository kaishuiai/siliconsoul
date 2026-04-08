import asyncio
import os
import sys
import tempfile

from openpyxl import Workbook

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.experts.cfo_expert import CFOExpert
from src.models.request_response import ExpertRequest


def _make_xlsx(path: str, rev: float, cost: float, ni: float, ta: float, tl: float, te: float) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "income"
    ws.append(["item", "value"])
    ws.append(["revenue", rev])
    ws.append(["cost", cost])
    ws.append(["net_income", ni])
    ws2 = wb.create_sheet("balance")
    ws2.append(["item", "value"])
    ws2.append(["total_assets", ta])
    ws2.append(["total_liabilities", tl])
    ws2.append(["total_equity", te])
    wb.save(path)


async def main() -> None:
    d = tempfile.mkdtemp()
    p1 = os.path.join(d, "a.xlsx")
    p2 = os.path.join(d, "b.xlsx")
    _make_xlsx(p1, 10000, 6000, 1500, 50000, 30000, 20000)
    _make_xlsx(p2, 12000, 7200, 1800, 54000, 32000, 22000)

    expert = CFOExpert()
    req = ExpertRequest(
        text="compare two reports",
        user_id="smoke",
        task_type="cfo_chat",
        extra_params={"file_paths": [p1, p2]},
    )
    res = await expert.analyze(req)
    print("error:", res.error)
    data = res.result or {}
    print("file_paths:", data.get("file_paths"))
    ind = data.get("indicators") or {}
    print("is_mock_data:", ind.get("is_mock_data"))
    print("values:", ind.get("values"))


if __name__ == "__main__":
    asyncio.run(main())
