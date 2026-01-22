# Prior Art Search Prototype

This folder contains a lightweight prototype for a prior art search service. It accepts uploads
(DOCX, PDF, PPTX, XLSX/CSV, or TXT) and returns the most similar patents based on TF-IDF cosine
similarity against a small example corpus. A simple HTML interface is included and optimized for
mobile browsers.

## Features

- Upload office documents and extract text.
- Rank similar patents from a JSON corpus.
- JSON API suitable for prototyping a UI or external integrations.
- Mobile-friendly HTML upload and results view.

## Getting Started

```bash
cd app
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## Example Request

```bash
curl -X POST "http://127.0.0.1:8000/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/document.pdf"
```

## Web UI

Visit `http://127.0.0.1:8000/` in a desktop or mobile browser to use the upload interface.

## Notes

- The example corpus is stored in `data/patents.json`. Replace this file with your patent corpus
  or connect to a database/vector index when moving to production.
- HWP (한글) files are not parsed by default. If you need HWP support, consider adding a parser
  such as `pyhwp` or an external conversion step to TXT/PDF before uploading.
