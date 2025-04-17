import json
import yaml
from config import (
    METRICS_CONFIG_FILE,
    GENERATED_RECIPES_FILE,
    GENERATED_SCORED_RECIPES_FILE,
)
from app.utils.logging import save_recipe_log
from app.evaluation.scoring import score_recipe
from app.utils.parser import parse_markdown_recipe

with open(METRICS_CONFIG_FILE) as f:
    METRICS_CONFIG_FILE = yaml.safe_load(f)

with open(GENERATED_RECIPES_FILE, "r") as f:
    data = json.load(f)

for item in data:
    if "recipe" in item and item["recipe"]:
        parsed = parse_markdown_recipe(item["recipe"])
        item["parsed"] = parsed
        item["scores"] = score_recipe(
            item, parsed["steps"], parsed["ingredients"]
        )
        filepath = save_recipe_log(item)
        print(f"📝 Logged recipe: {filepath}")
    else:
        item["scores"] = {"RScore": 0.0, "note": "No recipe text available"}

with open(GENERATED_SCORED_RECIPES_FILE, "w") as f:
    json.dump(data, f, indent=2)
