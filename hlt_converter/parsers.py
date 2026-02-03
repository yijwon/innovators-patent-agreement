"""Input parsers for different source formats."""

from __future__ import annotations

from pathlib import Path

from .extractors import (
    ExtractionError,
    extract_docx_text,
    extract_hwp_text,
    extract_pdf_text,
)
from .sections import normalize_heading


def parse_markdown(content: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current_key = "DESCRIPTION"
    sections.setdefault(current_key, [])

    for raw_line in content.splitlines():
        line = raw_line.rstrip()
        if line.lstrip().startswith("#"):
            heading_text = line.lstrip("#").strip()
            normalized = normalize_heading(heading_text)
            if normalized:
                current_key = normalized
                sections.setdefault(current_key, [])
                continue
        sections[current_key].append(line)

    return sections


def parse_plain_text(content: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current_key = "DESCRIPTION"
    sections.setdefault(current_key, [])

    for raw_line in content.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if stripped:
            normalized_heading = normalize_heading(stripped)
            if normalized_heading:
                current_key = normalized_heading
                sections.setdefault(current_key, [])
                continue
        if ":" in line:
            prefix, remainder = line.split(":", 1)
            normalized = normalize_heading(prefix)
            if normalized:
                current_key = normalized
                sections.setdefault(current_key, [])
                if remainder.strip():
                    sections[current_key].append(remainder.strip())
                continue
        sections[current_key].append(line)

    return sections


def parse_file(path: Path) -> dict[str, list[str]]:
    suffix = path.suffix.lower()

    if suffix in {".md", ".markdown"}:
        content = path.read_text(encoding="utf-8")
        return parse_markdown(content)
    if suffix in {".txt"}:
        content = path.read_text(encoding="utf-8")
        return parse_plain_text(content)
    if suffix in {".docx"}:
        content = extract_docx_text(path)
        return parse_plain_text(content)
    if suffix in {".pdf"}:
        content = extract_pdf_text(path)
        return parse_plain_text(content)
    if suffix in {".hwp"}:
        content = extract_hwp_text(path)
        return parse_plain_text(content)

    raise ExtractionError(f"Unsupported file extension: {path.suffix}")
