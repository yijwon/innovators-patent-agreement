"""Input parsers for different source formats."""

from __future__ import annotations

from pathlib import Path

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
    content = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()

    if suffix in {".md", ".markdown"}:
        return parse_markdown(content)
    if suffix in {".txt"}:
        return parse_plain_text(content)

    return parse_plain_text(content)
