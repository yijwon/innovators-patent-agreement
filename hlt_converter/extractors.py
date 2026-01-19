"""Text extractors for supported input formats."""

from __future__ import annotations

import subprocess
import zipfile
from pathlib import Path
from shutil import which
from xml.etree import ElementTree


class ExtractionError(RuntimeError):
    """Raised when an input file cannot be extracted."""


def extract_docx_text(path: Path) -> str:
    try:
        with zipfile.ZipFile(path) as archive:
            with archive.open("word/document.xml") as document:
                tree = ElementTree.parse(document)
    except (KeyError, zipfile.BadZipFile, OSError, ElementTree.ParseError) as exc:
        raise ExtractionError(f"Failed to read DOCX file: {path}") from exc

    paragraphs: list[str] = []
    for paragraph in tree.iterfind(".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"):
        texts = [
            node.text
            for node in paragraph.iterfind(
                ".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"
            )
            if node.text
        ]
        if texts:
            paragraphs.append("".join(texts))
        else:
            paragraphs.append("")

    return "\n".join(paragraphs)


def extract_pdf_text(path: Path) -> str:
    try:
        from pypdf import PdfReader  # type: ignore
    except ImportError as exc:
        raise ExtractionError(
            "pypdf is required to extract text from PDF files. "
            "Install it with: pip install pypdf"
        ) from exc

    try:
        reader = PdfReader(str(path))
    except Exception as exc:  # noqa: BLE001 - preserve extraction context
        raise ExtractionError(f"Failed to read PDF file: {path}") from exc

    return "\n".join(page.extract_text() or "" for page in reader.pages)


def extract_hwp_text(path: Path) -> str:
    tool = which("hwp5txt")
    if not tool:
        raise ExtractionError(
            "hwp5txt is required to extract text from HWP files. "
            "Install pyhwp (pip install pyhwp) to provide hwp5txt."
        )

    result = subprocess.run(
        [tool, str(path)],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise ExtractionError(
            f"hwp5txt failed to extract {path}: {result.stderr.strip()}"
        )

    return result.stdout
