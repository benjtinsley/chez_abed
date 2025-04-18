import json
from pathlib import Path
from tqdm import tqdm

SOURCE_FILE = Path(__file__).parent / "data" / "RecipeNLG_dataset.json"
TARGET_FILE = Path(__file__).parent / "data" / "abed_recipes.jsonl"


def infer_type(title):
    title = title.lower()
    if "cake" in title or "cookie" in title or "dessert" in title:
        return "dessert"
    if "salad" in title:
        return "lunch"
    if "soup" in title or "stew" in title:
        return "dinner"
    return "dinner"


def convert_entry(entry):
    title = entry["title"]
    ingredients = entry["ingredients"]
    instructions = entry.get("instructions", [])

    abed = {
        "flavor": [],  # Leave empty for now
        "texture": [],  # Leave empty for now
        "type": infer_type(title),
    }

    prompt = {
        "input": abed,
        "output": {
            "title": title,
            "ingredients": ingredients,
            "steps": instructions,
        },
    }
    return prompt


def main():
    with open(SOURCE_FILE) as f:
        data = json.load(f)

    with open(TARGET_FILE, "w") as out:
        for entry in tqdm(data, desc="Converting"):
            abed_entry = convert_entry(entry)
            out.write(json.dumps(abed_entry) + "\n")

    print(f"✅ Converted {len(data)} recipes to ABED format.")
    print(f"📝 Saved to {TARGET_FILE}")


if __name__ == "__main__":
    main()
