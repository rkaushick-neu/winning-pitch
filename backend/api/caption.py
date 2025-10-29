from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import os
import json
import re
from typing import List, Dict, Any
# import logging
from utils.logger import get_logger
from utils.gemini_vision import GeminiVisionClient

router = APIRouter()

# Base path for intermediate files
INTERMEDIATE_DIR = "./../data/intermediate"
os.makedirs(INTERMEDIATE_DIR, exist_ok=True)

# Set up logging
logger = get_logger("caption_images")

def extract_image_references(markdown_text: str) -> List[str]:
    """
    Extract image references from markdown text.
    Returns list of image IDs found in markdown.
    """
    # Pattern to match ![img-0.jpeg](img-0.jpeg) or similar
    pattern = r'!\[([^\]]+)\]\(([^)]+)\)'
    matches = re.findall(pattern, markdown_text)
    
    # Return the image IDs (second group in the match)
    return [match[1] for match in matches]

def replace_image_with_caption(markdown_text: str, image_id: str, caption: str) -> str:
    """
    Replace image markdown tag with caption text.
    """
    # Pattern to match the specific image reference
    pattern = rf'!\[{re.escape(image_id)}\]\({re.escape(image_id)}\)'
    
    # Replace with caption text
    return re.sub(pattern, caption, markdown_text)

def process_page_images(page: Dict[str, Any], gemini_client: GeminiVisionClient) -> Dict[str, Any]:
    """
    Process images in a single page and return updated page data.
    """
    if "images" not in page or not page["images"]:
        logger.info(f"Page {page.get('index', 'unknown')} has no images to process")
        return page
    
    # Extract image references from markdown
    markdown_text = page.get("markdown", "")
    image_references = extract_image_references(markdown_text)
    
    if not image_references:
        logger.info(f"Page {page.get('index', 'unknown')} has no image references in markdown")
        return page
    
    # Prepare image data for batch processing
    image_data_list = []
    for image in page["images"]:
        if image.get("id") in image_references:
            image_data_list.append({
                "id": image["id"],
                "image_base64": image.get("image_base64", "")
            })
    
    if not image_data_list:
        logger.info(f"Page {page.get('index', 'unknown')} has no matching images to process")
        return page
    
    # Get captions for all images
    logger.info(f"Processing {len(image_data_list)} images for page {page.get('index', 'unknown')}")
    captions = gemini_client.batch_caption_images(image_data_list)
    
    # Replace image references with captions
    updated_markdown = markdown_text
    for image_id, caption in captions.items():
        updated_markdown = replace_image_with_caption(updated_markdown, image_id, caption)
        logger.info(f"Replaced image {image_id} with caption: {caption[:100]}...")
    
    # Create updated page data
    updated_page = page.copy()
    updated_page["markdown"] = updated_markdown
    updated_page.pop("images", None) # removing the images list (which contains the entire base64 string)
    updated_page.pop("dimensions") # removing dimensions

    return updated_page

def process_markdown_file(file_path: str) -> Dict[str, Any]:
    """
    Process a single markdown JSON file and return results.
    """
    try:
        # Read the original file
        with open(file_path, 'r', encoding='utf-8') as file:
            markdown_data = json.load(file)
        
        # Initialize Gemini client
        gemini_client = GeminiVisionClient()
        
        # Process each page
        processed_pages = []
        total_images_processed = 0
        processed_page_indices = []
        
        for page in markdown_data.get("pages", []):
            page_index = page.get("index", len(processed_pages))
            
            # Process images in this page
            updated_page = process_page_images(page, gemini_client)
            processed_pages.append(updated_page)
            
            # Count images processed
            if "images" in page and page["images"]:
                page_image_count = len([img for img in page["images"] if img.get("id")])
                total_images_processed += page_image_count
                if page_image_count > 0:
                    processed_page_indices.append(page_index)
        
        # Create new data structure
        captioned_data = markdown_data.copy()
        captioned_data["pages"] = processed_pages
        
        # Save the captioned file automatically
        file_id = os.path.splitext(os.path.basename(file_path))[0]
        captioned_filename = f"{file_id}-captioned.json"
        captioned_file_path = os.path.join(INTERMEDIATE_DIR, captioned_filename)
        with open(captioned_file_path, 'w', encoding='utf-8') as outfile:
            json.dump(captioned_data, outfile, indent=2, ensure_ascii=False)
        logger.info(f"Captioned file saved successfully: {captioned_file_path}")
        
        return {
            "data": captioned_data,
            "total_images_processed": total_images_processed,
            "processed_page_indices": processed_page_indices
        }
        
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing markdown file: {str(e)}"
        )

# no longer in use
@router.post("/caption/all")
async def caption_all_markdowns():
    """
    Process all markdown JSON files and create captioned versions.
    """
    try:
        if not os.path.exists(INTERMEDIATE_DIR):
            return JSONResponse(
                content={
                    "message": "No markdown directory found",
                    "processed_files": [],
                    "total_files": 0
                },
                status_code=200
            )
        
        # Get all JSON files
        json_files = [f for f in os.listdir(INTERMEDIATE_DIR) if f.endswith('.json')]
        
        if not json_files:
            return JSONResponse(
                content={
                    "message": "No JSON files found in markdown directory",
                    "processed_files": [],
                    "total_files": 0
                },
                status_code=200
            )
        
        processed_files = []
        total_images_processed = 0
        
        for filename in json_files:
            file_id = os.path.splitext(filename)[0]
            file_path = os.path.join(INTERMEDIATE_DIR, filename)
            
            try:
                # Process the file
                result = process_markdown_file(file_path)
                
                processed_files.append({
                    "original_id": file_id,
                    "captioned_id": f"{file_id}-captioned",
                    "images_processed": result["total_images_processed"],
                    "processed_pages": result["processed_page_indices"]
                })
                
                total_images_processed += result["total_images_processed"]
                
                logger.info(f"Successfully processed {filename} -> {file_id}-captioned.json")
                
            except Exception as e:
                logger.error(f"Failed to process {filename}: {str(e)}")
                processed_files.append({
                    "original_id": file_id,
                    "error": str(e)
                })
        
        return JSONResponse(
            content={
                "message": f"Processed {len(json_files)} files",
                "processed_files": processed_files,
                "total_files": len(json_files),
                "total_images_processed": total_images_processed
            },
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"Error in caption_all_markdowns: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing all markdown files: {str(e)}"
        )

# no longer in use
@router.post("/caption/{markdown_id}")
async def caption_markdown_by_id(markdown_id: str):
    """
    Process a specific markdown file by ID and create a captioned version.
    """
    try:
        # Construct the file path
        file_path = os.path.join(INTERMEDIATE_DIR, f"{markdown_id}.json")
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail=f"Markdown file with ID '{markdown_id}' not found"
            )
        
        # Process the file
        result = process_markdown_file(file_path)
        
        return JSONResponse(
            content={
                "original_id": markdown_id,
                "captioned_id": f"{markdown_id}-captioned",
                "images_processed": result["total_images_processed"],
                "processed_pages": result["processed_page_indices"],
                "message": f"Successfully processed {markdown_id}.json -> {markdown_id}-captioned.json"
            },
            status_code=200
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in caption_markdown_by_id: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing markdown file {markdown_id}: {str(e)}"
        )
