# scoring.py – contains metric calculations for recipe evaluation
import re

def score_recipe(recipe_entry, seen_titles, seen_ingredient_fingerprints):
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
        "novelty": score_novelty(recipe_entry, seen_titles, seen_ingredient_fingerprints),
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
    steps = [line.strip().lower() for line in instructions.split("\n") if line.strip()]
    multitask_cues = ["while", "meanwhile", "as the", "during the"]

    out_of_order_phrases = [
        ("add", "chop"),     # bad: add onions before chopping them
        ("serve", "bake"),   # bad: serve before baking
        ("garnish", "cook"), # bad: garnish before cooking
    ]
    
    score = 1.0
    penalties = 0

    for phrase1, phrase2 in out_of_order_phrases:
        first = -1
        second = -1
        for i, step in enumerate(steps):
            if any(phrase in step.lower() for phrase in multitask_cues):
                # Allow multitasking during parallel actions
                continue
            if phrase1 in step and first == -1:
                first = i
            if phrase2 in step and second == -1:
                second = i
        if first != -1 and second != -1 and first < second:
            # print(f"[Coherence] '{phrase1}' found before '{phrase2}' at steps {first} < {second}")
            penalties += 1

    # Apply penalty for each detected inversion
    if penalties:
        score = max(0.0, 1.0 - 0.3 * penalties)

    return round(score, 2)

def score_cues(instructions):
    cues = [
        "until golden", "until soft", "until browned", "until crisp", "until tender",
        "until fragrant", "until bubbling", "until thickened", "until melted", "until reduced"
    ]
    instructions_lower = instructions.lower()
    found = set(cue for cue in cues if cue in instructions_lower)
    return round(len(found) / len(cues), 2)

def score_plausibility(instructions):
    # Placeholder: assume plausible unless known red flag is found
    implausible_phrases = ["microwave for 2 hours", "boil lettuce", "grill yogurt"]
    for bad in implausible_phrases:
        if bad in instructions.lower():
            return 0.0
    return 1.0

def jaccard_similarity_set(set_a, set_b):
    return len(set_a & set_b) / len(set_a | set_b)

def get_title_novelty(title, seen_titles):
    title_novelty = 1.0
    title_tokens = set(title.split())

    for seen in seen_titles:
        similarity = jaccard_similarity_set(title_tokens, seen)
        if similarity > 0.7:
            title_novelty = 0.0
            break
        if similarity > 0.3:
            title_novelty = 0.5
            break

    return (title_novelty, title_tokens)

def get_ingredient_novelty(ingredients, seen_ingredient_fingerprints):
    ingredient_novelty = 1.0
    ingredient_tokens = set(word for ing in ingredients for word in ing.split())

    for seen in seen_ingredient_fingerprints:
        overlap = len(seen.intersection(ingredient_tokens)) / max(len(seen.union(ingredient_tokens)), 1)
        if overlap > 0.9:
            ingredient_novelty = 0.0
            break
        if overlap > 0.6:
            ingredient_novelty = 0.5
            break

    return (ingredient_novelty, ingredient_tokens)

def score_novelty(recipe_entry, seen_titles, seen_ingredient_fingerprints):
    title = recipe_entry["recipe"].split("**Title:**")[1].split("\n")[0].strip().lower()
    ingredients = extract_ingredients(recipe_entry["recipe"])

    title_novelty, title_tokens = get_title_novelty(title, seen_titles)
    ingredient_novelty, ingredient_tokens = get_ingredient_novelty(ingredients, seen_ingredient_fingerprints)

    seen_titles.append(title_tokens)
    seen_ingredient_fingerprints.append(ingredient_tokens)

    novelty = 0.6 * ingredient_novelty + 0.4 * title_novelty
    # print(f"[Novelty] Title: {title}")
    # print(f"      Title Score: {title_novelty}\n      Ingredients Score: {ingredient_novelty}\n      Final Score: {novelty}")
    return novelty

def score_conciseness(instructions):
    lines = [line for line in instructions.split("\n") if line.strip()]
    repeated = sum(1 for i in range(1, len(lines)) if lines[i] == lines[i-1])
    return round(1 - repeated / len(lines), 2) if lines else 1.0