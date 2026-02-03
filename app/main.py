from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse

from extractors import get_extractor
from search import find_similar_patents, load_patents


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "patents.json"
UI_PATH = BASE_DIR / "ui.html"

app = FastAPI(title="Patent Prior Art Search")


@app.get("/", response_class=HTMLResponse)
async def root() -> HTMLResponse:
    return HTMLResponse(UI_PATH.read_text(encoding="utf-8"))


@app.post("/upload")
async def upload(file: UploadFile = File(...)) -> JSONResponse:
    if not file.filename:
        return JSONResponse(status_code=400, content={"error": "No filename provided."})

    file_bytes = await file.read()
    if not file_bytes:
        return JSONResponse(status_code=400, content={"error": "Empty file."})

    extractor = get_extractor(file.filename)
    text = extractor(file_bytes).strip()
    if not text:
        return JSONResponse(
            status_code=422,
            content={"error": "No extractable text found in the file."},
        )

    patents = load_patents(DATA_PATH)
    results = find_similar_patents(text, patents)

    return JSONResponse(
        content={
            "filename": file.filename,
            "excerpt": text[:500],
            "results": results,
        }
    )
