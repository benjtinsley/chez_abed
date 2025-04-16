import json
from dotenv import load_dotenv
import openai
from config import (
    PROMPTS_FILE,
    TEMPLATE_PROMPT_FILE,
    GENERATED_RECIPES_FILE,
    DEFAULT_MODEL,
    TEMPERATURE,
    MAX_TOKENS,
)

load_dotenv()

# Load abstraction prompts
with open(PROMPTS_FILE, "r") as f:
    abstraction_sets = json.load(f)

# Load base prompt template
with open(TEMPLATE_PROMPT_FILE, "r") as f:
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
    if "mood" in entry:
        parts.append(f"- Mood: {entry['mood']}")
    if "dietary_restrictions" in entry and entry["dietary_restrictions"]:
        parts.append(f"- Diet: {entry['dietary_restrictions']}")
    if "total_served" in entry:
        parts.append(f"- Total Served: {entry['total_served']}")
    if "technique_level" in entry:
        parts.append(f"- Technique Level: {entry['technique_level']}")
    if "prep_time" in entry:
        parts.append(f"- Prep Time: {entry['prep_time']}")

    descriptor_block = "\n".join(parts)
    return template.replace("{descriptors}", descriptor_block)


for entry in abstraction_sets:
    filled_prompt = build_prompt(base_prompt, entry)

    client = openai.OpenAI()

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
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
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
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
with open(GENERATED_RECIPES_FILE, "w") as f:
    json.dump(generated, f, indent=2)
