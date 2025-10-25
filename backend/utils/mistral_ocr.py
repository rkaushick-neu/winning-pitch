import os
import base64
import requests
import json
import io
from dotenv import load_dotenv
from mistralai import Mistral, DocumentURLChunk
from mistralai.models import OCRResponse
from pathlib import Path


load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

def replace_images_in_markdown(markdown_str: str, images_dict: dict) -> str:
    """
    Replace image placeholders in markdown with base64-encoded images.

    Args:
        markdown_str: Markdown text containing image placeholders
        images_dict: Dictionary mapping image IDs to base64 strings

    Returns:
        Markdown text with images replaced by base64 data
    """
    for img_name, base64_str in images_dict.items():
        markdown_str = markdown_str.replace(
            f"![{img_name}]({img_name})", f"![{img_name}]({base64_str})"
        )
    return markdown_str

def get_combined_markdown(ocr_response: OCRResponse) -> str:
    """
    Combine OCR text and images into a single markdown document.

    Args:
        ocr_response: Response from OCR processing containing text and images

    Returns:
        Combined markdown string with embedded images
    """
    markdowns: list[str] = []
    # Extract images from page
    for page in ocr_response.pages:
        image_data = {}
        for img in page.images:
            image_data[img.id] = img.image_base64
        # Replace image placeholders with actual images
        markdowns.append(replace_images_in_markdown(page.markdown, image_data))

    return "\n\n".join(markdowns)

def perform_ocr_on_pdf(pdf_content: bytes, filename: str) -> str:
    """Send PDF directly to Mistral for OCR/text extraction."""
    
    client = Mistral(api_key=MISTRAL_API_KEY)

    # Upload PDF to Mistral
    uploaded_file = client.files.upload(
        file={
            "file_name": filename,
            "content": pdf_content,
        },
        purpose="ocr",
    )

    # Get URL for the uploaded file
    signed_url = client.files.get_signed_url(file_id=uploaded_file.id, expiry=1)

    # Process PDF with OCR, including embedded images
    pdf_response = client.ocr.process(
        document=DocumentURLChunk(document_url=signed_url.url),
        model="mistral-ocr-latest",
        include_image_base64=True
    )

    response_dict = json.loads(pdf_response.model_dump_json())

    # Create dynamic filename based on input filename
    base_filename = os.path.splitext(filename)[0]  # Remove extension
    output_filename = f"{base_filename}-ocr-response.json"
    
    # Save JSON response to a file in the data/markdown directory
    output_file = Path("./../data/markdown") / output_filename
    output_file.parent.mkdir(parents=True, exist_ok=True)  # Create directory if it doesn't exist

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(response_dict, f, indent=4, ensure_ascii=False)

    print(f"\nJSON response saved to: {output_file}")
    return str(output_file)


# TODO: Test ocr on images
def perform_ocr_on_images(images: list) -> str:
    """For PPT/PPTX slides converted to images."""
    all_text = ""
    for i, image in enumerate(images):
        # Convert PIL Image to bytes
        img_buffer = io.BytesIO()
        image.save(img_buffer, format="PNG")
        img_b64 = base64.b64encode(img_buffer.getvalue()).decode("utf-8")

        payload = {
            "model": "mistral-ocr",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract all readable text from this image accurately."},
                        {"type": "image_url", "image_url": f"data:image/png;base64,{img_b64}"}
                    ]
                }
            ],
            "temperature": 0.0
        }

        headers = {
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(MISTRAL_API_KEY, json=payload, headers=headers)
        data = response.json()

        try:
            text = data["choices"][0]["message"]["content"]
        except Exception:
            text = "[OCR Error or Empty Response]"

        all_text += f"\n---\n{text}"
    return all_text.strip()
