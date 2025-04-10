import re
import yaml
import csv
from config import METRICS_CONFIG_FILE, GENERATIONS_LOG_FILE

# Load metric config from YAML
with open(METRICS_CONFIG_FILE) as f:
    METRICS_CONFIG_FILE = yaml.safe_load(f)

MEASURE_WORDS = [
    "tsp",
    "tbsp",
    "teaspoon",
    "tablespoon",
    "cup",
    "cups",
    "oz",
    "ounce",
    "ounces",
    "pint",
    "quart",
    "gallon",
    "ml",
    "liter",
    "liters",
    "grams",
    "g",
    "kg",
    "pound",
    "lb",
    "lbs",
    "dash",
    "pinch",
    "can",
    "cans",
    "package",
    "packages",
]

PREP_METHODS = [
    "minced",
    "chopped",
    "diced",
    "sliced",
    "crushed",
    "grated",
    "peeled",
    "halved",
    "shredded",
    "zested",
    "mashed",
    "beaten",
    "whisked",
    "blended",
    "rinsed",
    "drained",
    "to",
    "taste",
    "and",
]

STOPWORDS = set(MEASURE_WORDS + PREP_METHODS)


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
        "ingredient_usage_completeness": score_ingredient_usage(
            ingredients_list, instructions_text
        ),
        "instruction_coherence": score_instruction_coherence(
            instructions_text
        ),
        "cues": score_cues(instructions_text),
        "plausibility": score_plausibility(instructions_text),
        "novelty": score_novelty(recipe_entry),
        "conciseness": score_conciseness(instructions_text),
    }

    # Weights for each metric
    weights = METRICS_CONFIG_FILE["weights"]

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
    return [
        line.strip().lower()
        for line in ingredients_block.split("\n")
        if line.strip().startswith("-")
    ]


def extract_instructions(recipe_text):
    match = re.search(
        r"\*\*Instructions:\*\*(.*?)\n\n|\Z", recipe_text, re.DOTALL
    )
    if not match:
        return ""
    return match.group(1).strip()


def score_ingredient_usage(ingredients, instructions):
    # Score based on % of ingredients mentioned in instructions
    mentioned = sum(
        1
        for ing in ingredients
        if any(word in instructions.lower() for word in ing.split())
    )
    return round(mentioned / len(ingredients), 2) if ingredients else 0


def score_instruction_coherence(instructions):
    # Brute force check for out-of-order instructions
    steps = [
        line.strip().lower()
        for line in instructions.split("\n")
        if line.strip()
    ]
    multitask_cues = ["while", "meanwhile", "as the", "during the"]

    out_of_order_phrases = [
        ("add", "chop"),  # bad: add onions before chopping them
        ("serve", "bake"),  # bad: serve before baking
        ("garnish", "cook"),  # bad: garnish before cooking
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
            # print(
            #     f"[Coherence] '{phrase1}'"
            #     "found before '{phrase2}'"
            #     "at steps {first} < {second}"
            # )
            penalties += 1

    # Apply penalty for each detected inversion
    if penalties:
        score = max(0.0, 1.0 - 0.3 * penalties)

    return round(score, 2)


def score_cues(instructions):
    # Brute force check for cooking cues
    cues = [
        "until",
        "when",
        "after",
        "before",
        "while",
        "as",
        "during",
        "then",
        "next",
        "finally",
    ]
    instructions_lower = instructions.lower()
    found = set(cue for cue in cues if cue in instructions_lower)
    return round(len(found) / len(cues), 2)


def score_plausibility(instructions):
    # Brute force check for implausible instructions
    # assume plausible unless known red flag is found
    implausible_phrases = [
        "microwave for 2 hours",
        "boil lettuce",
        "grill yogurt",
    ]
    for bad in implausible_phrases:
        if bad in instructions.lower():
            return 0.0
    return 1.0


def extract_ingredient_name(line):
    # Remove bullet, lowercase, remove punctuation
    line = re.sub(r"[^a-zA-Z\s]", "", line.lower().strip("- "))
    tokens = line.split()

    # Filter out quantities and techniques
    filtered = [
        word
        for word in tokens
        if word not in STOPWORDS and not word.isnumeric()
    ]
    return " ".join(filtered)


def jaccard_similarity_set(set_a, set_b):
    return len(set_a & set_b) / len(set_a | set_b)


def score_novelty(recipe_entry):
    log_path = GENERATIONS_LOG_FILE

    # Quick check to create log if it doesn't exist
    if not log_path.exists():
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["title", "ingredients"])
            writer.writeheader()

    title = (
        recipe_entry["recipe"]
        .split("**Title:**")[1]
        .split("\n")[0]
        .strip()
        .lower()
    )
    ingredients = extract_ingredients(recipe_entry["recipe"])
    title_tokens = set(title.split())
    ingredient_tokens = set(
        word
        for ing in ingredients
        for word in extract_ingredient_name(ing).split()
    )

    # Read existing logs
    existing_titles = []
    existing_ingredients = []
    if log_path.exists():
        with open(log_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_titles.append(set(row["title"].split()))
                existing_ingredients.append(set(row["ingredients"].split()))
    else:
        # Create log with headers
        with open(log_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["title", "ingredients"])
            writer.writeheader()

    # Calculate novelty
    config = METRICS_CONFIG_FILE["novelty_thresholds"]

    title_score = 1.0
    for seen in existing_titles:
        similarity = jaccard_similarity_set(title_tokens, seen)
        if similarity > config["title"]["hard_penalty"]:
            title_score = 0.0
            break
        elif similarity > config["title"]["soft_penalty"]:
            title_score = 0.5
            break

    ingredient_score = 1.0
    for seen in existing_ingredients:
        similarity = jaccard_similarity_set(ingredient_tokens, seen)
        if similarity > config["ingredients"]["hard_penalty"]:
            ingredient_score = 0.0
            break
        elif similarity > config["ingredients"]["soft_penalty"]:
            ingredient_score = 0.5
            break

    # Write current to log
    with open(log_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "ingredients"])
        writer.writerow(
            {
                "title": " ".join(title_tokens),
                "ingredients": " ".join(ingredient_tokens),
            }
        )

    novelty = (
        config["weighting"]["title"] * title_score
        + config["weighting"]["ingredients"] * ingredient_score
    )
    return round(novelty, 2)


def score_conciseness(instructions):
    lines = [line for line in instructions.split("\n") if line.strip()]
    repeated = sum(1 for i in range(1, len(lines)) if lines[i] == lines[i - 1])
    return round(1 - repeated / len(lines), 2) if lines else 1.0
