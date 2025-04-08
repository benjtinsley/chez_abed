# scoring.py – contains metric calculations for recipe evaluation
import re

def score_recipe(recipe_entry):
    """
    Score a single recipe entry from the generated_recipes.json file.

    Parameters:
    - recipe_entry (dict): contains "input", "prompt", "recipe"

    Returns:
    - dict: dictionary of individual metric scores and weighted total
    """
    recipe_text = recipe_entry.get("recipe", "")
    ingredients_list = extract_ingredients(recipe_text)
    instructions_text = extract_instructions(recipe_text)

    scores = {
        "ingredient_usage_completeness": score_ingredient_usage(ingredients_list, instructions_text),
        "instruction_coherence": score_instruction_coherence(instructions_text),
        "cues": score_cues(instructions_text),
        "plausibility": score_plausibility(instructions_text),
        "novelty": score_novelty(recipe_entry),
        "conciseness": score_conciseness(instructions_text)
    }

    # Weights for each metric
    weights = {
        "ingredient_usage_completeness": 0.25,
        "instruction_coherence": 0.25,
        "plausibility": 0.2,
        "conciseness": 0.15,
        "cues": 0.05,
        "novelty": 0.05
    }

    total = sum(scores[k] * weights.get(k, 0) for k in scores)
    scores["MScore"] = round(total, 4)
    return scores

# Stub functions (to be implemented)
def extract_ingredients(recipe_text):
    # Return a list of lowercased ingredient lines
    match = re.search(r"\*\*Ingredients:\*\*(.*?)\*\*", recipe_text, re.DOTALL)
    if not match:
        return []
    ingredients_block = match.group(1)
    return [line.strip().lower() for line in ingredients_block.split("\n") if line.strip().startswith("-")]

def extract_instructions(recipe_text):
    match = re.search(r"\*\*Instructions:\*\*(.*?)\n\n|\Z", recipe_text, re.DOTALL)
    if not match:
        return ""
    return match.group(1).strip()

def score_ingredient_usage(ingredients, instructions):
    # Score based on % of ingredients mentioned in instructions
    mentioned = sum(1 for ing in ingredients if any(word in instructions.lower() for word in ing.split()))
    return round(mentioned / len(ingredients), 2) if ingredients else 0

def score_instruction_coherence(instructions):
    # Placeholder: always return 1 for now
    return 1.0

def score_cues(instructions):
    cues = ["until golden", "until soft", "until browned", "until crisp", "until tender"]
    found = any(cue in instructions.lower() for cue in cues)
    return 1.0 if found else 0.0

def score_plausibility(instructions):
    # Placeholder: assume plausible unless known red flag is found
    implausible_phrases = ["microwave for 2 hours", "boil lettuce", "grill yogurt"]
    for bad in implausible_phrases:
        if bad in instructions.lower():
            return 0.0
    return 1.0

def score_novelty(recipe_entry):
    # Placeholder: always return 1 for now
    return 1.0

def score_conciseness(instructions):
    lines = [line for line in instructions.split("\n") if line.strip()]
    repeated = sum(1 for i in range(1, len(lines)) if lines[i] == lines[i-1])
    return round(1 - repeated / len(lines), 2) if lines else 1.0