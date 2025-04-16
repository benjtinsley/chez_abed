import re
from typing import Dict


def parse_markdown_recipe(markdown: str) -> Dict[str, any]:
    """
    Parse a markdown-formatted recipe into structured data.
    Returns a dictionary with title, description, ingredients, steps, and tags.
    """
    result = {
        "title": "",
        "description": "",
        "ingredients": [],
        "steps": [],
        "tags": {},
    }

    # Normalize line endings and split by line
    lines = markdown.strip().splitlines()

    current_section = None
    for line in lines:
        line = line.strip()

        # Match sections
        if line.startswith("**Title:**"):
            result["title"] = line.replace("**Title:**", "").strip()

        elif line.startswith("**Description:**"):
            current_section = "description"
            result["description"] = line.replace(
                "**Description:**", ""
            ).strip()

        elif line.startswith("**Ingredients:**"):
            current_section = "ingredients"

        elif line.startswith("**Instructions:**"):
            current_section = "steps"

        elif line.startswith("**Tags:**"):
            current_section = "tags"
            tag_line = line.replace("**Tags:**", "").strip()
            tag_parts = [t.strip() for t in tag_line.split("|")]
            for part in tag_parts:
                if "=" in part:
                    key, value = part.split("=")
                    result["tags"][key.strip()] = [
                        v.strip() for v in value.split(",")
                    ]

        elif current_section == "ingredients" and line.startswith("-"):
            result["ingredients"].append(line.lstrip("- ").strip())

        elif current_section == "steps" and re.match(r"^\d+\.", line):
            result["steps"].append(line)

    return result
