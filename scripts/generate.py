import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent.parent

# File paths
PROMPTS_FILE = ROOT_DIR / "data/abed_prompts.json"
TEMPLATE_FILE = ROOT_DIR / "prompts/base_prompt_template.txt"
OUTPUT_DIR = ROOT_DIR / "data/generated_recipes.json"

# Load abstraction prompts
with open(PROMPTS_FILE, "r") as f:
    abstraction_sets = json.load(f)

# Load base prompt template
with open(TEMPLATE_FILE, "r") as f:
    base_prompt = f.read()

# Collect generations
generated = []

def build_prompt(template, entry):
    parts = []
    if "flavor" in entry and entry["flavor"]:
        parts.append(f"- Flavor: {', '.join(entry['flavor'])}")
    if "texture" in entry and entry["texture"]:
        parts.append(f"- Texture: {', '.join(entry['texture'])}")
    if "type" in entry:
        parts.append(f"- Type: {entry['type']}")
    descriptor_block = "\n".join(parts)
    return template.replace("{descriptors}", descriptor_block)

for entry in abstraction_sets:
    filled_prompt = build_prompt(base_prompt, entry)

    # For now, just print it (later: send to OpenAI or similar)
    print("==== Prompt ====")
    print(filled_prompt)
    print()

    # Optionally, store prompt in case we batch generate later
    generated.append({
        "input": entry,
        "prompt": filled_prompt,
        "recipe": None  # Will be filled after model response
    })

# Save the prompts for review
with open(OUTPUT_DIR, "w") as f:
    json.dump(generated, f, indent=2)
