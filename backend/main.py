from fastapi import FastAPI, UploadFile, File
from api.ingest import router as ingest_router
from api.markdown import router as markdown_router

app = FastAPI(title="Winning PitchDeck")
app.include_router(ingest_router, prefix="/api")
app.include_router(markdown_router, prefix="/api")
