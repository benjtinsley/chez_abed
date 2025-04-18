import json
from pathlib import Path
from datasets import load_dataset
from sentence_transformers import SentenceTransformer

# Create training data directory
target_data_dir = Path("app/training/data")
target_data_dir.mkdir(parents=True, exist_ok=True)

# Manually parse the text file from the dataset
print("📦 Downloading RecipeNLG from Hugging Face...")
dataset = load_dataset("B2111797/recipenlg-text-256")
raw_path = Path(dataset["train"].cache_files[0]["filename"])
lines = Path(raw_path).read_text(encoding="latin-1").split("<RECIPE_END>")

parsed_recipes = []
for entry in lines:
    if "<RECIPE_START>" not in entry:
        continue

    title = ""
    ingredients = []
    instructions = []

    try:
        if "<TITLE_START>" in entry:
            title = (
                entry.split("<TITLE_START>")[1].split("<TITLE_END>")[0].strip()
            )

        if "<INPUT_START>" in entry:
            raw_ingredients = entry.split("<INPUT_START>")[1].split(
                "<INPUT_END>"
            )[0]
            ingredients = [
                i.strip()
                for i in raw_ingredients.split("<NEXT_INPUT>")
                if i.strip()
            ]

        if "<INSTR_START>" in entry:
            raw_steps = entry.split("<INSTR_START>")[1].split("<INSTR_END>")[0]
            instructions = [
                s.strip() for s in raw_steps.split("<NEXT_INSTR>") if s.strip()
            ]

        parsed_recipes.append(
            {
                "title": title,
                "ingredients": ingredients,
                "instructions": instructions,
            }
        )
    except Exception as e:
        print("⚠️ Failed to parse a recipe:", e)
        continue

# Save the parsed data
dataset_path = target_data_dir / "RecipeNLG_dataset.json"
with open(dataset_path, "w") as f:
    json.dump(parsed_recipes, f, indent=2)

print(f"✅ Parsed and saved {len(parsed_recipes)} recipes to {dataset_path}")

# Create training script stubs if they don't exist
for filename in ["prepare_data.py", "finetune_model.py", "evaluate_model.py"]:
    fpath = Path("app/training") / filename
    fpath.touch(exist_ok=True)

print("🏗️  Training setup complete!")

# Pre-download sentence-transformers model to avoid delay later
print("🧠 Downloading SentenceTransformer model 'all-MiniLM-L6-v2'...")

SentenceTransformer("all-MiniLM-L6-v2")
print("✅ SentenceTransformer model downloaded and ready.")
