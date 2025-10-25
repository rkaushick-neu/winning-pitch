from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from agents.research_agent import research_agent

router = APIRouter()

class ResearchRequest(BaseModel):
    company_name: str
    # pitch_data: dict  # This should be OCR + captioned JSON
    markdown_id: str # This should be the Markdown ID to the OCR + captioned JSON

@router.post("/generate-research")
async def generate_research(request: ResearchRequest):
    try:
        markdown_report = research_agent(request.markdown_id, request.company_name)
        return {"report": markdown_report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))