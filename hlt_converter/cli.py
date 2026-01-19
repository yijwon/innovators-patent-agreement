"""Command line interface for converting files to HLT format."""

from __future__ import annotations

import argparse
from pathlib import Path

from .hlt_writer import write_hlt
from .parsers import parse_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Convert source documents into Korean patent specification HLT format."
        )
    )
    parser.add_argument("source", type=Path, help="Input file to convert")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Destination HLT file (defaults to <source>.hlt)",
    )
    parser.add_argument(
        "--title",
        help="Optional title override for the HLT metadata",
    )
    parser.add_argument(
        "--language",
        default="ko",
        help="Language tag for the output (default: ko)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.source.exists():
        parser.error(f"Source file not found: {args.source}")

    output_path = args.output or args.source.with_suffix(".hlt")
    sections = parse_file(args.source)
    write_hlt(
        output_path,
        sections,
        title=args.title,
        language=args.language,
        source_path=args.source,
    )
    print(f"HLT written to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
