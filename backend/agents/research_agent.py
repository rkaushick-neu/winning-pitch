import json
import os
from agents.tools.perplexity_search import perplexity_search
from openai import OpenAI

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY"))

def research_agent(json_path: str, company_name: str):
    with open(f"./../data/markdown/{json_path}.json", "r") as f:
        pitch_data = json.load(f)

    # Updated to handle merged OCR + caption JSON
    pages = pitch_data.get("pages", [])
    context = "\n\n".join([page["markdown"] for page in pages if page.get("markdown")])

    # Step 1: Perform web enrichment
    print("Searching Perplexity for background info...")
    # search_result = perplexity_search(f"{company_name} startup overview life sciences funding team patents")
    search_result = perplexity_search(
        f"{company_name} life science startup overview founders team background advisors funding rounds investors technology intellectual property patents product development clinical trials market landscape competitors differentiation traction customers partnerships publications regulatory approvals"
    )

    print(f"\nRESEARCH AGENT: Perplexity Search Result: \n{search_result}")

    # Step 2: Generate structured markdown using ChatGPT/Claude
    print("Generating investment summary...")
    messages = [
        {
            "role": "system",
            "content": (
                "You are an AI research assistant preparing a due diligence summary for investment managers at BoxOne Ventures."
                "Use the given pitch deck text and image captions, along with the web findings, to produce a factual and analytical markdown report "
                "under these sections:\n\n"
                "- Overview\n- Founders & Team\n- Technology & IP\n- Product & Traction\n- Market Landscape\n- Investment Rationale\n- Risks / Open Questions\n- Contact Information\n\n"
                "Be concise, avoid marketing fluff, and cite URLs where relevant. Use markdown hyperlinks for all sources."
                " Retain clickable markdown links inline instead of replacing them with reference numbers."
                " Example: Use the format [[TechCrunch](https://techcrunch.com/abc)] to link sources directly in the text.\n\n"
                "Guardrails:\n"
                "1. Only include information that appears in the pitch deck or cited web sources. If data is missing or unclear, explicitly state “Not available” rather than inferring or fabricating.\n"
                "2. Every factual statement sourced from the web must include an inline markdown citation in the format [Source Name](URL). Do not replace links with reference numbers or generic text like “according to sources.”\n"
                "3. Avoid marketing tone or speculative language. Focus on facts, defensibility, and investment relevance — e.g., technology moat, team credibility, IP ownership, and regulatory hurdles.\n"
                "4. Strictly follow the given markdown section structure. If a section lacks data, include the section header and write “No verifiable information found.” Do not merge or skip sections."            )
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