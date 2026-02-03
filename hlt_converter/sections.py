"""Section metadata and normalization rules for HLT output."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SectionDefinition:
    key: str
    title: str
    aliases: tuple[str, ...]


SECTION_DEFINITIONS = (
    SectionDefinition(
        key="TITLE",
        title="발명의 명칭",
        aliases=("title", "발명의 명칭", "제목"),
    ),
    SectionDefinition(
        key="TECHNICAL_FIELD",
        title="기술분야",
        aliases=("technical field", "field", "기술분야", "기술 분야"),
    ),
    SectionDefinition(
        key="BACKGROUND",
        title="배경기술",
        aliases=("background", "background art", "배경기술", "배경"),
    ),
    SectionDefinition(
        key="SUMMARY",
        title="발명의 요약",
        aliases=("summary", "요약", "발명의 요약"),
    ),
    SectionDefinition(
        key="DESCRIPTION",
        title="발명의 상세한 설명",
        aliases=("detailed description", "description", "상세한 설명", "발명의 상세한 설명"),
    ),
    SectionDefinition(
        key="CLAIMS",
        title="청구항",
        aliases=("claims", "claim", "청구항"),
    ),
    SectionDefinition(
        key="ABSTRACT",
        title="초록",
        aliases=("abstract", "초록"),
    ),
)


def normalize_heading(heading: str) -> str | None:
    normalized = heading.strip().lower()
    for definition in SECTION_DEFINITIONS:
        if normalized == definition.key.lower():
            return definition.key
        if normalized == definition.title.lower():
            return definition.key
        if normalized in {alias.lower() for alias in definition.aliases}:
            return definition.key
    return None


def section_title(section_key: str) -> str:
    for definition in SECTION_DEFINITIONS:
        if definition.key == section_key:
            return definition.title
    return section_key
