import json
import os
from agents.tools.perplexity_search import perplexity_search
from openai import OpenAI
from utils.prompt_loader import load_prompt

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY"))

def research_agent(json_path: str, company_name: str) -> str:
    with open(f"./../data/markdown/{json_path}.json", "r") as f:
        pitch_data = json.load(f)

    # Updated to handle merged OCR + caption JSON
    pages = pitch_data.get("pages", [])
    context = "\n\n".join([page["markdown"] for page in pages if page.get("markdown")])

    # Step 1: Perform web enrichment
    print("Searching Perplexity for background info...")
    # search_result = perplexity_search(f"{company_name} startup overview life sciences funding team patents")
    search_result = perplexity_search(
        f"{company_name} startup overview founders team background advisors funding rounds investors technology intellectual property patents product development clinical trials market landscape competitors differentiation traction customers partnerships publications regulatory approvals"
    )

    print(f"\nRESEARCH AGENT: Perplexity Search Result: \n{search_result}")

    system_prompt = load_prompt("research_agent/v1")
    # Step 2: Generate structured markdown using ChatGPT/Claude
    print("Generating investment summary...")
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": (
                f"# Pitch Deck (merged OCR of text + image captions):\n{context}\n\nWeb Findings:\n{search_result['summary']}"
                f"# Web Findings:\n{search_result['summary']}\n\n"
                # f"Citations:\n{', '.join(search_result.get('citations', []))}"
            )
        }
    ]

    # print(f"\nRESEARCH AGENT: User Prompt Message: \n {messages[1]['content']}")

    response = client.chat.completions.create(
        model="google/gemini-2.5-flash",
        messages=messages,
        temperature=0.3
    )

    markdown_output = response.choices[0].message.content
    # os.makedirs("./../data/markdown", exist_ok=True)

    output_path = f"./../data/markdown/{company_name.lower().replace(' ', '_')}_summary.md"
    with open(output_path, "w") as f:
        f.write(markdown_output)

    print(f"✅ Report saved at: {output_path}")
    return markdown_output