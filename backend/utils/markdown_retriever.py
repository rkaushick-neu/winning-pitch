import re
from typing import Dict, List

def extract_from_pitch_json(pitch_data: dict) -> Dict[str, str]:
    """
    Extracts and organizes markdown content into sections using top-level headings (e.g., #, ##).
    """
    pages = pitch_data.get("pages", [])
    full_markdown = "\n\n".join(page.get("markdown", "") for page in pages)

    # Split content into sections using top-level headers
    sections = split_markdown_by_headers(full_markdown)
    return sections

def split_markdown_by_headers(text: str) -> Dict[str, str]:
    """
    Splits markdown into a dictionary of sections based on H1 (#) or H2 (##) headers.
    If no headers exist, everything goes under 'General Notes'.
    """
    section_pattern = re.compile(r"(?m)^#{1,2} (.+)$")
    matches = list(section_pattern.finditer(text))

    if not matches:
        return {"General Notes": text.strip()}

    sections = {}
    for i, match in enumerate(matches):
        section_title = match.group(1).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        content = text[start:end].strip()
        sections[section_title] = content

    return sections