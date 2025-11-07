from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import json
from utils.mistral_ocr import perform_ocr_on_pdf
from utils.gemini_vision import GeminiVisionClient
from api.caption import process_markdown_file  # reuse existing logic if possible
from utils.logger import get_logger
from agents.research_agent import research_agent
# from utils.vector_store import store_in_qdrant


router = APIRouter()

INTERMEDIATE_DIR = "./../data/intermediate"
os.makedirs(INTERMEDIATE_DIR, exist_ok=True)


# log_file_path = os.path.join(LOG_DIR, "process_pitchdeck.log")

logger = get_logger("process_pitchdeck")

@router.post("/process/pitchdeck")
async def process_pitchdeck(file: UploadFile = File(...)):
    """
    End-to-end pipeline:
    1. Run OCR the uploaded pitch deck (PDF)
    3. Run image captioning on the OCR result
    5. Research enrichment (LLM + Perplexity)
    6. Save Markdown summary
    """
    try:
        filename = file.filename
        ext = os.path.splitext(filename)[-1].lower()
        file_id = os.path.splitext(filename)[0]

        if ext not in [".pdf"]:
            raise HTTPException(status_code=400, detail="Only PDF files supported currently")

        # Step 1: Run OCR
        file_content = await file.read()
        logger.info("Processing Pitch Deck: Starting OCR...")
        print("Processing Pitch Deck: Starting OCR...")
        ocr_result_path = perform_ocr_on_pdf(file_content, filename)
        logger.info(f"OCR result saved to {ocr_result_path}")

        # Step 2: Captioning
        logger.info("Starting image captioning...")
        print("Starting image captioning...")
        captioned_data = process_markdown_file(ocr_result_path)
        captioned_file_path = os.path.join(INTERMEDIATE_DIR, f"{file_id}-ocr-response-captioned.json")

        with open(captioned_file_path, 'w', encoding='utf-8') as f:
            json.dump(captioned_data["data"], f, indent=2, ensure_ascii=False)
        
        logger.info(f"OCR image captioned file saved to {captioned_file_path}")
        print(f"OCR image captioned file saved to {captioned_file_path}")

        # return JSONResponse(
        #     content={
        #         "file_id": file_id,
        #         "message": "Pitch deck successfully processed (OCR + Caption)",
        #         "ocr_path": ocr_target_path,
        #         "captioned_path": captioned_file_path,
        #         "images_processed": captioned_data["total_images_processed"]
        #     },
        #     status_code=200
        # )

        # Step 2.5: Store OCR + Captioned text in Qdrant
        # logger.info("Embedding pitch deck OCR + captions into Qdrant...")
        # for item in captioned_data["data"]:
        #     # Convert string → dict if needed
        #     if isinstance(item, str):
        #         try:
        #             print(item)
        #             item = json.loads(item)
        #         except json.JSONDecodeError:
        #             logger.warning(f"Skipping malformed JSON item: {item[:100]}")
        #             continue
        #     text_chunk = item.get("markdown", "")
        #     if text_chunk:
        #         store_in_qdrant(text_chunk, {
        #             "text": text_chunk,
        #             "source": "pitchdeck_pdf",
        #             "source_detail": filename,
        #             "company_name": file_id,
        #             "stage": "ocr_caption"
        #         })
        # logger.info("Stored pitch deck text into Qdrant.")

        # Step 3: Research enrichment
        logger.info("Starting research enrichment...")
        markdown_output = research_agent(json_path=f"{file_id}-ocr-response-captioned", company_name=file_id)
        final_md_path = os.path.join("./../data/markdown", f"{file_id}_summary.md")

        with open(final_md_path, 'w', encoding='utf-8') as md_file:
            md_file.write(markdown_output)

        logger.info(f"Markdown report saved to {final_md_path}")

        return JSONResponse(
            content={
                "file_id": file_id,
                "message": "Pitch deck successfully processed (OCR + Caption + Research)",
                "markdown": markdown_output,
                "ocr_path": ocr_result_path,
                "captioned_path": captioned_file_path,
                "final_md_id": f"{file_id}_summary"
            },
            status_code=200
        )


    except Exception as e:
        logger.error(f"Error in process_pitchdeck: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing pitch deck: {str(e)}")