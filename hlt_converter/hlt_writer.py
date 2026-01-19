"""HLT output generator."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from .sections import section_title


def render_hlt(
    sections: dict[str, list[str]],
    *,
    title: str | None,
    language: str,
    source_path: Path,
) -> str:
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    lines: list[str] = []
    lines.append("HLT/1.0")
    lines.append("@META")
    if title:
        lines.append(f"Title: {title}")
    lines.append(f"Language: {language}")
    lines.append(f"Source-File: {source_path.name}")
    lines.append(f"Generated-At: {timestamp}")
    lines.append("")

    for key, content_lines in sections.items():
        if not content_lines:
            continue
        lines.append(f"@SECTION {key}")
        lines.append(f"# {section_title(key)}")
        lines.extend(content_lines)
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def write_hlt(
    output_path: Path,
    sections: dict[str, list[str]],
    *,
    title: str | None,
    language: str,
    source_path: Path,
) -> None:
    output_path.write_text(
        render_hlt(sections, title=title, language=language, source_path=source_path),
        encoding="utf-8",
    )
