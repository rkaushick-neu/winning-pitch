import re
import requests
import os
from utils.prompt_loader import load_prompt

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def perplexity_search(query: str) -> dict:
    """
    Calls Perplexity API via OpenRouter to perform a web search with citations.
    """
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    system_prompt = load_prompt("perplexity_search/v1")
    payload = {
        "model": "perplexity/sonar",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Search the web and summarize: {query}. Include citation URLs in markdown format."}
        ]
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        print(f"❌ Perplexity Error: {response.text}")
        return {"summary": "Search failed.", "citations": []}

    data = response.json()
    text = data["choices"][0]["message"]["content"]

    # Extract citation URLs from markdown links and plain URLs reliably
    # md_links = re.findall(r'\[.*?\]\((https?://[^\s)]+)\)', text)
    # plain_urls = re.findall(r'(?<!\()https?://[^\s)>\]]+', text)
    # citations = list(set(md_links + plain_urls))

    # print(f"PERPLEXITY SEARCH: Citations --> {citations}")

    return {
        "summary": text.strip(),
        # "citations": citations
    }