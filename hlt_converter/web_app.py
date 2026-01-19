"""Simple HTML interface for converting files to HLT."""

from __future__ import annotations

import cgi
import html
import os
import tempfile
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
    </style>
  </head>
  <body>
    <h1>HLT 변환기</h1>
    <p class="note">Word(.docx), PDF, HWP, Markdown, 텍스트 파일을 HLT 포맷으로 변환합니다.</p>
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


def main() -> None:
    server = HTTPServer(("0.0.0.0", 8000), HLTRequestHandler)
    print("HLT converter running at http://localhost:8000")
    server.serve_forever()


if __name__ == "__main__":
    main()
