import os

def load_prompt(prompt_name: str) -> str:
    base_path = os.path.join(os.path.dirname(__file__), "..", "prompts")
    path = os.path.join(base_path, f"{prompt_name}.txt")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        raise ValueError(f"Prompt file not found: {path}")