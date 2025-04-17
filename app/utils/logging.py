from pathlib import Path
from datetime import datetime
import re
from config import LOGS_DIR


def sanitize_filename(title):
    return re.sub(r"[^\w\-]", "_", title.lower())


def save_recipe_log(recipe: dict, log_dir: Path = LOGS_DIR):
    generated = recipe.get("recipe", {})
    timestamp = datetime.now()

    year = timestamp.strftime("%Y")
    month = timestamp.strftime("%m")
    day = timestamp.strftime("%d")
    time_str = timestamp.strftime("%H-%M-%S%f")[:-3]

    log_dir = LOGS_DIR / year / month / day
    log_dir.mkdir(parents=True, exist_ok=True)

    title = "untitled"
    if isinstance(generated, dict):
        title = generated.get("title", "untitled")
    elif isinstance(generated, str):
        # Try to extract title from the first line if markdown
        match = re.search(r"\*\*Title:\*\*\s*(.*)", generated)
        if match:
            title = match.group(1).strip()

    filename = f"{time_str}_{sanitize_filename(title)}.md"
    filepath = log_dir / filename

    with open(filepath, "w") as f:
        if isinstance(generated, str):
            f.write(generated)
        elif isinstance(generated, dict):
            f.write(f"# {title}\n\n")
            # optionally include ingredients and steps from the dict here

        if "scores" in recipe:
            f.write(
                "\n\n---\n\n**RScore:** {:.2f}\n".format(
                    recipe["scores"].get("RScore", 0.0)
                )
            )
            for key, val in recipe["scores"].items():
                if key != "RScore":
                    emoji = "✅" if val > 0.6 else "❌"
                    f.write(f"- {key.capitalize()}: {emoji} ({val:.2f})\n")

    return filepath
