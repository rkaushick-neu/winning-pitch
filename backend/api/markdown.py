from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import os
import json
from typing import List, Dict, Any

router = APIRouter()

# Base path for markdown files
MARKDOWN_DIR = "./../data/markdown"

@router.get("/markdowns")
async def get_all_markdowns():
    """
    Get a list of all markdown files in the data/markdown directory
    """
    try:
        if not os.path.exists(MARKDOWN_DIR):
            return JSONResponse(
                content={"markdowns": [], "count": 0},
                status_code=200
            )
        
        markdown_files = []
        for filename in os.listdir(MARKDOWN_DIR):
            if filename.endswith('.md'):
                file_path = os.path.join(MARKDOWN_DIR, filename)
                file_stats = os.stat(file_path)
                
                # Extract a basic identifier from filename (without extension)
                file_id = os.path.splitext(filename)[0]
                
                markdown_files.append({
                    "id": file_id,
                    "filename": filename,
                    "size": file_stats.st_size,
                    "created": file_stats.st_ctime,
                    "modified": file_stats.st_mtime
                })
        
        # Sort by modification time (newest first)
        markdown_files.sort(key=lambda x: x["modified"], reverse=True)
        
        return JSONResponse(
            content={
                "markdowns": markdown_files,
                "count": len(markdown_files)
            },
            status_code=200
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving markdown files: {str(e)}"
        )

@router.get("/markdowns/{markdown_id}")
async def get_markdown_by_id(markdown_id: str):
    """
    Get a specific markdown file by its ID
    """
    try:
        # Construct the file path
        file_path = os.path.join(MARKDOWN_DIR, f"{markdown_id}.md")
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail=f"Markdown file with ID '{markdown_id}' not found"
            )
        
        # Read the markdown file content as a string
        with open(file_path, 'r', encoding='utf-8') as file:
            markdown_content = file.read()
        
        return {
            "id": markdown_id,
            "markdown": markdown_content
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving markdown file: {str(e)}"
        )

@router.get("/markdowns/{markdown_id}/pages")
async def get_markdown_pages(markdown_id: str):
    """
    Get all pages from a specific markdown file
    """
    try:
        file_path = os.path.join(MARKDOWN_DIR, f"{markdown_id}.md")
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail=f"Markdown file with ID '{markdown_id}' not found"
            )
        
        with open(file_path, 'r', encoding='utf-8') as file:
            markdown_content = file.read()
        
        return {
            "id": markdown_id,
            "markdown": markdown_content
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving markdown pages: {str(e)}"
        )

@router.get("/markdowns/{markdown_id}/pages/{page_index}")
async def get_markdown_page_by_index(markdown_id: str, page_index: int):
    """
    Get a specific page from a markdown file by page index
    """
    try:
        file_path = os.path.join(MARKDOWN_DIR, f"{markdown_id}.md")
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=404,
                detail=f"Markdown file with ID '{markdown_id}' not found"
            )
        
        with open(file_path, 'r', encoding='utf-8') as file:
            markdown_content = file.read()
        
        return {
            "id": markdown_id,
            "markdown": markdown_content
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving markdown page: {str(e)}"
        )
