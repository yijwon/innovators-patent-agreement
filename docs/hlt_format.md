# HLT 포맷 개요

HLT는 한국특허 명세서 생성을 위한 텍스트 기반 포맷입니다. 이 저장소에서는 실무에서 바로 활용할 수 있도록 최소한의 구조와 메타데이터를 정의했습니다.

## 기본 구조

```
HLT/1.0
@META
Title: 발명의 명칭
Language: ko
Source-File: original.md
Generated-At: 2024-01-01T12:34:56+00:00

@SECTION TITLE
# 발명의 명칭
...

@SECTION TECHNICAL_FIELD
# 기술분야
...
```

## 섹션 규칙

- `@META`는 생성 도구가 자동으로 채우는 메타데이터 영역입니다.
- `@SECTION <KEY>`는 본문 섹션의 시작을 의미합니다.
- 섹션 키는 아래 표준 키를 사용합니다.

| 키 | 의미 |
| --- | --- |
| TITLE | 발명의 명칭 |
| TECHNICAL_FIELD | 기술분야 |
| BACKGROUND | 배경기술 |
| SUMMARY | 발명의 요약 |
| DESCRIPTION | 발명의 상세한 설명 |
| CLAIMS | 청구항 |
| ABSTRACT | 초록 |

## 변환 규칙

- Markdown의 제목(`#`, `##` 등)은 대응되는 섹션 키로 매핑됩니다.
- 텍스트 파일의 `제목:`, `기술분야:` 같은 라벨은 해당 섹션을 시작합니다.
- 매핑되지 않은 내용은 `DESCRIPTION` 섹션으로 이동합니다.

필요하다면 섹션 키와 매핑 규칙을 추가하여 조직 내부 형식에 맞게 확장할 수 있습니다.
