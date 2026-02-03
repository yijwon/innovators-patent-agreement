"""Simple HTML interface for converting files to HLT."""

from __future__ import annotations

import argparse
import cgi
import html
import os
import tempfile
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from .extractors import ExtractionError
from .hlt_writer import render_hlt
from .parsers import parse_file

HTML_PAGE = """<!doctype html>
<html lang="ko">
  <head>
    <meta charset="utf-8" />
    <title>HLT 변환기</title>
    <style>
      body { font-family: sans-serif; margin: 2rem; }
      form { display: grid; gap: 1rem; max-width: 480px; }
      label { font-weight: 600; }
      input[type="text"] { width: 100%; padding: 0.5rem; }
      button { padding: 0.6rem 1rem; }
      .note { color: #555; font-size: 0.9rem; }
      .steps { background: #f6f6f6; padding: 0.75rem; border-radius: 8px; }
    </style>
  </head>
  <body>
    <h1>HLT 변환기</h1>
    <p class="note">Word(.docx), PDF, HWP, Markdown, 텍스트 파일을 HLT 포맷으로 변환합니다.</p>
    <div class="steps">
      <strong>사용 방법</strong>
      <ol>
        <li>파일을 선택합니다.</li>
        <li>필요하면 발명의 명칭/언어를 입력합니다.</li>
        <li>아래 버튼 한 번 클릭으로 HLT를 다운로드합니다.</li>
      </ol>
    </div>
    <form action="/convert" method="post" enctype="multipart/form-data">
      <div>
        <label for="file">입력 파일</label><br />
        <input type="file" id="file" name="file" required />
      </div>
      <div>
        <label for="title">발명의 명칭(선택)</label><br />
        <input type="text" id="title" name="title" placeholder="예: 발명의 명칭" />
      </div>
      <div>
        <label for="language">언어 태그</label><br />
        <input type="text" id="language" name="language" value="ko" />
      </div>
      <button type="submit">HLT 다운로드</button>
    </form>
  </body>
</html>
"""


class HLTRequestHandler(BaseHTTPRequestHandler):
    server_version = "HLTConverter/0.1"

    def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler naming
        if self.path not in {"/", "/index.html"}:
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
            return

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML_PAGE.encode("utf-8"))

    def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler naming
        if self.path != "/convert":
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
            return

        content_type = self.headers.get("Content-Type", "")
        if "multipart/form-data" not in content_type:
            self.send_error(HTTPStatus.BAD_REQUEST, "Invalid content type")
            return

        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={"REQUEST_METHOD": "POST", "CONTENT_TYPE": content_type},
        )
        if "file" not in form:
            self.send_error(HTTPStatus.BAD_REQUEST, "Missing file upload")
            return

        upload = form["file"]
        filename = Path(upload.filename or "input").name
        title = form.getfirst("title", "") or None
        language = form.getfirst("language", "ko") or "ko"

        suffix = Path(filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(upload.file.read())
            temp_path = Path(temp_file.name)

        try:
            sections = parse_file(temp_path)
        except ExtractionError as exc:
            self._send_error_page(str(exc), HTTPStatus.BAD_REQUEST)
            return
        finally:
            try:
                os.remove(temp_path)
            except OSError:
                pass

        hlt_content = render_hlt(
            sections,
            title=title,
            language=language,
            source_path=Path(filename),
        )
        output_name = f"{Path(filename).stem or 'output'}.hlt"

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header(
            "Content-Disposition", f'attachment; filename="{output_name}"'
        )
        self.end_headers()
        self.wfile.write(hlt_content.encode("utf-8"))

    def _send_error_page(self, message: str, status: HTTPStatus) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        escaped = html.escape(message)
        self.wfile.write(
            f"<html><body><h1>Error</h1><p>{escaped}</p></body></html>".encode("utf-8")
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the HLT web converter.")
    parser.add_argument("--host", default="0.0.0.0", help="Bind host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Bind port (default: 8000)")
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Do not open the browser automatically",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    server = HTTPServer((args.host, args.port), HLTRequestHandler)
    url = f"http://localhost:{args.port}"
    print(f"HLT converter running at {url}")
    if not args.no_open:
        webbrowser.open(url)
    server.serve_forever()


if __name__ == "__main__":
    main()
