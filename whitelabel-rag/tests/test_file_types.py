"""Upload file types: the industry-standard document set.

The upload pipeline accepts PDF, Word, text, Markdown, CSV, HTML,
PowerPoint, Excel, EPUB, RTF, OpenDocument and JSON, and it guides
users with old Office formats (.doc/.xls/.ppt) and Google Docs link
files (.gdoc) to an uploadable file instead of a bare rejection.

Regression pinned here: PDF extraction once called ``pypdf.PdfReader``
while only ``PyPDF2`` was imported, so every PDF upload raised a
NameError that was swallowed and the file ingested 0 chunks.
"""

import io
import json
import zipfile

import pytest

from app.services.document_processor import DocumentProcessor
from app.utils.file_utils import ALLOWED_EXTENSIONS, validate_file_upload


def make_pdf(path, text):
    """Build a minimal valid PDF containing one line of text.

    Offsets for the xref table are computed as the file is built, so
    PyPDF2 can actually parse it.
    """
    stream = ("BT /F1 24 Tf 100 700 Td (%s) Tj ET" % text).encode()
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out += ("%d 0 obj\n" % i).encode() + obj + b"\nendobj\n"
    xref_pos = len(out)
    out += ("xref\n0 %d\n" % (len(objects) + 1)).encode()
    out += b"0000000000 65535 f \n"
    for off in offsets:
        out += ("%010d 00000 n \n" % off).encode()
    out += ("trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF"
            % (len(objects) + 1, xref_pos)).encode()
    path.write_bytes(bytes(out))


def build_files(tmp_path):
    """Create one real file of each supported type, all containing
    the same marker sentence."""
    marker = "zebra migration starts in March"
    files = {}

    p = tmp_path / "doc.pdf"
    make_pdf(p, marker)
    files["pdf"] = p

    from docx import Document
    doc = Document()
    doc.add_paragraph(marker)
    p = tmp_path / "doc.docx"
    doc.save(str(p))
    files["docx"] = p

    p = tmp_path / "doc.txt"
    p.write_text(marker)
    files["txt"] = p

    p = tmp_path / "doc.md"
    p.write_text("# Heading\n\n" + marker)
    files["md"] = p

    p = tmp_path / "doc.csv"
    p.write_text("animal,month\nzebra,March\n")
    files["csv"] = p

    p = tmp_path / "doc.html"
    p.write_text("<html><body><p>%s</p></body></html>" % marker)
    files["html"] = p

    from pptx import Presentation
    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    slide.shapes.add_textbox(10, 10, 400, 100).text_frame.text = marker
    p = tmp_path / "doc.pptx"
    prs.save(str(p))
    files["pptx"] = p

    import pandas as pd
    p = tmp_path / "doc.xlsx"
    pd.DataFrame({"animal": ["zebra"], "month": ["March"]}).to_excel(
        str(p), index=False)
    files["xlsx"] = p

    p = tmp_path / "doc.epub"
    with zipfile.ZipFile(p, "w") as book:
        book.writestr("mimetype", "application/epub+zip")
        book.writestr("OEBPS/content.xhtml",
                      "<html><body><p>%s</p></body></html>" % marker)
    files["epub"] = p

    p = tmp_path / "doc.rtf"
    p.write_text(r"{\rtf1\ansi %s}" % marker)
    files["rtf"] = p

    p = tmp_path / "doc.odt"
    with zipfile.ZipFile(p, "w") as doc:
        doc.writestr(
            "content.xml",
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<office:document-content xmlns:office="urn:oasis:names:tc:'
            'opendocument:xmlns:office:1.0" xmlns:text="urn:oasis:names:'
            'tc:opendocument:xmlns:text:1.0"><office:body><office:text>'
            '<text:p>%s</text:p></office:text></office:body>'
            '</office:document-content>' % marker)
    files["odt"] = p

    p = tmp_path / "doc.json"
    p.write_text(json.dumps({"note": marker}))
    files["json"] = p

    return files, marker


@pytest.mark.parametrize("kind", [
    "pdf", "docx", "txt", "md", "csv", "html",
    "pptx", "xlsx", "epub", "rtf", "odt", "json",
])
def test_each_supported_type_extracts_text(tmp_path, kind):
    files, marker = build_files(tmp_path)
    text = DocumentProcessor()._extract_text(str(files[kind]))
    assert marker.split()[0] in text or "zebra" in text, kind


def test_pdf_extraction_actually_works(tmp_path):
    """The old code called pypdf.PdfReader with only PyPDF2 imported,
    so every PDF silently ingested 0 chunks. This must return text."""
    files, marker = build_files(tmp_path)
    text = DocumentProcessor()._extract_text(str(files["pdf"]))
    assert marker in text


def test_supported_formats_match_allowlist():
    assert set(DocumentProcessor().get_supported_formats()) == ALLOWED_EXTENSIONS
    assert ALLOWED_EXTENSIONS == {
        'txt', 'pdf', 'docx', 'md', 'csv',
        'html', 'htm', 'pptx', 'xlsx', 'epub', 'rtf', 'odt', 'json',
    }


class FakeUpload:
    def __init__(self, filename):
        self.filename = filename


@pytest.mark.parametrize("filename,expected", [
    ("old.doc", ".docx"),
    ("old.xls", ".xlsx"),
    ("old.ppt", ".pptx"),
    ("notes.gdoc", "Download"),
])
def test_guided_formats_tell_user_what_to_do(filename, expected):
    valid, message = validate_file_upload(FakeUpload(filename))
    assert valid is False
    assert expected in message


def test_unknown_type_lists_what_is_allowed():
    valid, message = validate_file_upload(FakeUpload("archive.exe"))
    assert valid is False
    assert "pdf" in message and "docx" in message


def test_upload_endpoint_rejects_doc_with_guidance(client):
    resp = client.post(
        "/api/documents/upload_and_ingest_document",
        data={"file": (io.BytesIO(b"fake"), "old.doc")},
        content_type="multipart/form-data")
    assert resp.status_code == 400
    assert ".docx" in resp.get_json()["error"]


def test_upload_endpoint_rejects_unknown_type_with_list(client):
    resp = client.post(
        "/api/documents/upload_and_ingest_document",
        data={"file": (io.BytesIO(b"fake"), "archive.exe")},
        content_type="multipart/form-data")
    assert resp.status_code == 400
    assert "pdf" in resp.get_json()["error"]


def test_home_file_picker_lists_supported_types(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b'accept=".txt,.pdf,.docx' in resp.data
