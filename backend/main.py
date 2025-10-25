from fastapi import FastAPI, UploadFile, File
from api.ingest import router as ingest_router
from api.markdown import router as markdown_router
from api.caption import router as caption_router
from api.research import router as research_router

app = FastAPI(title="Winning PitchDeck")
app.include_router(ingest_router, prefix="/api")
app.include_router(markdown_router, prefix="/api")
app.include_router(caption_router, prefix="/api")
app.include_router(research_router, prefix="/api")