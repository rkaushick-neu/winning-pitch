import os
from pdf2image import convert_from_bytes
from pptx import Presentation
from PIL import Image
import io

def convert_to_images(file_content: bytes, filename: str) -> list[Image.Image]:
    ext = os.path.splitext(filename)[-1].lower()
    images = []

    if ext == ".pdf":
        pages = convert_from_bytes(file_content)
        images.extend(pages)

    elif ext in [".ppt", ".pptx"]:
        prs = Presentation(io.BytesIO(file_content))
        for slide in prs.slides:
            # Export each slide as image (using PIL)
            slide_image = _render_slide_as_image(slide)
            if slide_image:
                images.append(slide_image)
    else:
        raise ValueError("Unsupported file type.")
    return images

def _render_slide_as_image(slide):
    # TODO: Check if I need to complete this for PPT logic to work
    # Basic placeholder for slide-to-image logic
    # For more accurate rendering, consider `unoconv` or headless LibreOffice
    img = Image.new("RGB", (1280, 720), color=(255, 255, 255))
    return img
