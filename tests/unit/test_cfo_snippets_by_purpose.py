import zipfile

import pytest

from src.experts.cfo_expert import CFOExpert
from src.models.request_response import ExpertRequest


def _write_docx(path: str, text: str) -> None:
    document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:r><w:t>{text}</w:t></w:r></w:p>
  </w:body>
</w:document>
"""
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("word/document.xml", document_xml)


@pytest.mark.asyncio
async def test_cfo_returns_snippets_by_purpose_and_appends_evidence_section(tmp_path):
    p1 = tmp_path / "rev.docx"
    p2 = tmp_path / "cost.docx"
    _write_docx(str(p1), "分部收入：1000 万元；渠道 A")
    _write_docx(str(p2), "成本明细：履约成本 400 万元")

    expert = CFOExpert()
    req = ExpertRequest(
        text="请分析收入与成本结构",
        user_id="u1",
        task_type="cfo_chat",
        extra_params={
            "file_paths": [str(p1), str(p2)],
            "file_tags_by_path": {
                str(p1): {"purpose": "分部/产品收入"},
                str(p2): {"purpose": "成本明细"},
            },
            "business_context": {"period": "2024", "scope": "合并", "include_allocations": False},
        },
    )
    res = await expert.analyze(req)
    assert res.error is None
    out = res.result or {}
    sbp = out.get("snippets_by_purpose")
    assert isinstance(sbp, dict)
    assert "分部/产品收入" in sbp
    assert "成本明细" in sbp

    report = str(out.get("analysis_report") or "")
    assert "材料依据（按用途）" in report
    assert "分部/产品收入" in report
