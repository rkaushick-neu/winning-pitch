import json
import os
from agents.tools.perplexity_search import perplexity_search
from openai import OpenAI
from utils.prompt_loader import load_prompt
from utils.logger import get_logger

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENROUTER_API_KEY"))

# Base path for intermediate files
INTERMEDIATE_DIR = "./../data/intermediate"

logger = get_logger("research_agent")

def research_agent(json_path: str, company_name: str) -> str:
    with open(f"{INTERMEDIATE_DIR}/{json_path}.json", "r") as f:
        pitch_data = json.load(f)

    # Updated to handle merged OCR + caption JSON
    pages = pitch_data.get("pages", [])
    context = "\n\n".join([page["markdown"] for page in pages if page.get("markdown")])

    # Step 1: Perform web enrichment
    logger.info("Searching Perplexity for background info...")
    # search_result = perplexity_search(f"{company_name} startup overview life sciences funding team patents")
    search_result = perplexity_search(company_name)

    logger.info(f"Perplexity Search Result: {search_result}")

    # load system and user prompts
    system_prompt_template = load_prompt("research_agent/v2_system") 
    system_prompt = system_prompt_template.format(company_name=company_name)
    user_prompt_template = load_prompt("research_agent/v1_user")
    user_prompt = user_prompt_template.format(company_name=company_name, pitch_deck_context=context, web_search_results=search_result["summary"])

    # Step 2: Generate structured markdown using ChatGPT/Claude
    logger.info("Generating investment summary...")
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]

    # print(f"\nRESEARCH AGENT: User Prompt Message: \n {messages[1]['content']}")

    response = client.chat.completions.create(
        model="openai/gpt-4o",
        messages=messages,
        temperature=0.3
    )

    markdown_output = response.choices[0].message.content
    # os.makedirs("./../data/markdown", exist_ok=True)

    output_path = f"./../data/markdown/{company_name.lower().replace(' ', '_')}_summary.md"
    with open(output_path, "w") as f:
        f.write(markdown_output)

    logger.info(f"Report saved at: {output_path}")
    return markdown_output