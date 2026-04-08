import zipfile

from src.cfo.tools import parse_financial_document


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


def _write_pptx(path: str, text: str) -> None:
    slide_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
       xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:sp>
        <p:txBody>
          <a:p><a:r><a:t>{text}</a:t></a:r></a:p>
        </p:txBody>
      </p:sp>
    </p:spTree>
  </p:cSld>
</p:sld>
"""
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("ppt/slides/slide1.xml", slide_xml)


def test_parse_docx_extracts_text(tmp_path):
    p = tmp_path / "a.docx"
    _write_docx(str(p), "毛利率：40%")
    out = parse_financial_document(str(p))
    assert "毛利率" in (out.get("text") or "")


def test_parse_pptx_extracts_text(tmp_path):
    p = tmp_path / "a.pptx"
    _write_pptx(str(p), "收入增长 20%")
    out = parse_financial_document(str(p))
    assert "收入增长" in (out.get("text") or "")
