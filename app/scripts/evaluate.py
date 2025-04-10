from pathlib import Path
import json
import yaml
from app.utils.logging import save_recipe_log
from app.evaluation.scoring import score_recipe

# Load metric config from YAML
ROOT_DIR = Path(__file__).resolve().parents[2]
with open(ROOT_DIR / "app" / "evaluation" / "metrics_config.yaml") as f:
    METRIC_CONFIG = yaml.safe_load(f)

INPUT_FILE = ROOT_DIR / "data" / "generated_recipes.json"
OUTPUT_FILE = ROOT_DIR / "data" / "generated_scored_recipes.json"

with open(INPUT_FILE, "r") as f:
    data = json.load(f)


for item in data:
    if "recipe" in item and item["recipe"]:
        item["scores"] = score_recipe(item)
        filepath = save_recipe_log(item, ROOT_DIR)
        print(f"📝 Logged recipe: {filepath}")
    else:
        item["scores"] = {"MScore": 0.0, "note": "No recipe text available"}

with open(OUTPUT_FILE, "w") as f:
    json.dump(data, f, indent=2)
