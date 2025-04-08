# evaluate.py – evaluate generated recipes using custom rubric
import sys
import json
from pathlib import Path

# Add the project root to Python's module search path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from evaluation.scoring import score_recipe

ROOT_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = ROOT_DIR / "data/generated_recipes.json"
OUTPUT_FILE = ROOT_DIR /  "data/scored_recipes.json"

with open(INPUT_FILE, "r") as f:
    data = json.load(f)

for item in data:
    if "recipe" in item and item["recipe"]:
        item["scores"] = score_recipe(item)
    else:
        item["scores"] = {"MScore": 0.0, "note": "No recipe text available"}

with open(OUTPUT_FILE, "w") as f:
    json.dump(data, f, indent=2)

print("✅ Scoring complete. Results saved to scored_recipes.json")