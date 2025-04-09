import json
from pathlib import Path
from dotenv import load_dotenv
import openai

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parents[2]

# File paths
PROMPTS_FILE = ROOT_DIR / "data" / "abed_prompts.json"
TEMPLATE_FILE = ROOT_DIR / "prompts" / "base_prompt_template.txt"
OUTPUT_FILE = ROOT_DIR / "data" / "generated_recipes.json"

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

    client = openai.OpenAI()

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful culinary assistant that turns abstract "
                    "descriptors into complete recipes."
                ),
            },
            {"role": "user", "content": filled_prompt},
        ],
        temperature=0.8,
    )

    recipe_output = response.choices[0].message.content

    # Optionally, store prompt in case we batch generate later
    generated.append(
        {
            "input": entry,
            "prompt": filled_prompt,
            "recipe": recipe_output,  # Will be filled after model response
        }
    )

# Save the prompts for review
with open(OUTPUT_FILE, "w") as f:
    json.dump(generated, f, indent=2)
