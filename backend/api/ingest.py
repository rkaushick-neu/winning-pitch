from fastapi import APIRouter, UploadFile, File
from utils.mistral_ocr import perform_ocr_on_pdf, perform_ocr_on_images
from utils.convert_to_images import convert_to_images
import os

router = APIRouter()

@router.post("/ingest")
async def ingest_file(file: UploadFile = File(...)):
    # Read file content into memory
    file_content = await file.read()
    filename = file.filename
    
    ext = os.path.splitext(filename)[-1].lower()
    print(f"Processing file: {filename} with extension: {ext}")
    
    if ext == ".pdf":
        extracted_text_location = perform_ocr_on_pdf(file_content, filename)
        # Extract the file ID from the saved path for easy retrieval
        file_id = os.path.splitext(filename)[0]  # Remove extension
        return {
            "status": "Successfully extracted the Markdown",
            "file_id": file_id,
            "saved_location": extracted_text_location,
            "message": f"Markdown saved as {file_id}-ocr-response.json"
        }
    elif ext in [".ppt", ".pptx"]:
        # images = convert_to_images(file_content, filename)
        # extracted_text = perform_ocr_on_images(images)
        # For PPT/PPTX files, we might need to save the extracted text as well
        # For now, returning the extracted text directly
        return {
            "status": "PPT/ PPTX extraction WIP",
            # "extracted_text": extracted_text,
            # "message": "Text extracted from presentation slides"
        }
    else:
        return {"error": "Unsupported file type"}
