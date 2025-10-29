import re
import requests
import os
from utils.prompt_loader import load_prompt
from utils.logger import get_logger
from utils.vector_store import store_in_qdrant

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

logger = get_logger("perplexity_search")

def perplexity_search(company_name: str) -> dict:
    """
    Calls Perplexity API via OpenRouter to perform a web search with citations.
    """
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    # load system and user prompts
    system_prompt = load_prompt("perplexity_search/v2_system")
    user_prompt_template = load_prompt("perplexity_search/v1_user")
    user_prompt = user_prompt_template.format(company_name=company_name)

    payload = {
        "model": "perplexity/sonar-pro",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        logger.error(f"Perplexity Error: {response.text}")
        return {"summary": "Search failed.", "citations": []}

    data = response.json()
    text = data["choices"][0]["message"]["content"]

    # Extract citation URLs from markdown links and plain URLs reliably
    # md_links = re.findall(r'\[.*?\]\((https?://[^\s)]+)\)', text)
    # plain_urls = re.findall(r'(?<!\()https?://[^\s)>\]]+', text)
    # citations = list(set(md_links + plain_urls))

    # print(f"PERPLEXITY SEARCH: Citations --> {citations}")

    # After getting 'text' from Perplexity
    # logger.info("Parsing structured Perplexity output...")

    # # Primary pattern: Expected structured format
    # pattern = r"\*\*Summary:\*\*\s*(.*?)\s*\n\s*\*\*Source:\*\*\s*(https?://[^\s]+)"
    # matches = re.findall(pattern, text, re.DOTALL)

    # if not matches:
    #     logger.warning("Structured format not detected, attempting fallback regex parsing...")
    #     # Fallback: extract inline markdown links like [text](url)
    #     inline_pattern = r"(?:\*\*Summary:\*\*\s*)?(.*?)\s*\[.*?\]\((https?://[^\s)]+)\)"
    #     matches = re.findall(inline_pattern, text, re.DOTALL)


    # logger.info(f"Found {len(matches)} summary–source pairs in Perplexity output.")

    # for summary, url in matches:
    #     clean_summary = summary.strip()
    #     clean_url = url.strip()
    #     if clean_summary:
    #         store_in_qdrant(clean_summary, {
    #             "text": clean_summary,
    #             "source": "website_url",
    #             "source_detail": clean_url,
    #             "company_name": company_name,
    #             "stage": "perplexity_search"
    #         })
    # logger.info("Stored structured Perplexity results into Qdrant.")

    return {
        "summary": text.strip(),
        # "citations": citations
    }