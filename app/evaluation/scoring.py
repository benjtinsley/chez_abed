import re
import yaml
import csv
from config import METRICS_CONFIG_FILE, GENERATIONS_LOG_FILE

# Load metric config from YAML
with open(METRICS_CONFIG_FILE) as f:
    METRICS_CONFIG_FILE = yaml.safe_load(f)

FLAVOR_KEYWORDS = {
    "sweet": ["sugar", "honey", "syrup", "molasses", "maple"],
    "tangy": ["lemon", "lime", "vinegar", "pickled", "tamarind"],
    "salty": ["salt", "soy sauce", "brine"],
    "peppery": ["chili", "pepper", "hot sauce", "jalapeno"],
    "spiced": [
        "cinnamon",
        "cumin",
        "garlic",
        "onion",
        "ginger",
        "nutmeg",
        "clove",
    ],
    "fatty": ["butter", "cream", "bacon", "oil"],
    "bitter": ["coffee", "dark chocolate", "kale"],
    "earthy": ["mushroom", "truffle", "miso", "soy"],
}

TEXTURE_KEYWORDS = {
    "crispy": ["crisp", "crunch", "bake", "fry"],
    "chewy": ["chewy", "doughy", "stretchy"],
    "creamy": ["cream", "custard", "puree", "smooth"],
    "fluffy": ["fluffy", "airy", "whipped"],
    "juicy": ["juicy", "moist", "dripping"],
    "smooth": ["smooth", "silky"],
    "dry": ["dry", "crumbly"],
    "soft": ["soft", "tender"],
    "grainy": ["grainy", "grain", "rice", "course"],
}

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


def score_recipe(recipe_entry, parsed_steps, parsed_ingredients):
    """
    Score a single recipe entry from the generated_recipes.json file.

    Parameters:
    - recipe_entry (dict): contains "input", "prompt", "recipe"

    Returns:
    - dict: dictionary of individual metric scores and weighted total
    """
    normalized_ingredients = [
        extract_ingredient_name(ing) for ing in parsed_ingredients
    ]

    scores = {
        "ingredient_usage_completeness": score_ingredient_usage(
            normalized_ingredients, parsed_steps
        ),
        "instruction_coherence": score_instruction_coherence(parsed_steps),
        "cues": score_cues(parsed_steps),
        "plausibility": score_plausibility(parsed_steps),
        "novelty": score_novelty(recipe_entry),
        "conciseness": score_conciseness(parsed_steps),
        "abed_alignment": score_abed_alignment(
            recipe_entry, parsed_steps, parsed_ingredients
        ),
    }

    # Weights for each metric
    weights = METRICS_CONFIG_FILE["weights"]

    total = sum(scores[k] * weights.get(k, 0) for k in scores)
    scores["RScore"] = round(total, 4)
    return scores


def score_ingredient_usage(ingredients, steps):
    # Score based on % of ingredients mentioned in instructions
    instructions_text = " ".join(steps)
    mentioned = sum(
        1
        for ing in ingredients
        if all(word in instructions_text.lower() for word in ing.split())
    )
    return round(mentioned / len(ingredients), 2) if ingredients else 0


def score_instruction_coherence(steps):
    # Brute force check for out-of-order instructions
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
            penalties += 1

    # Apply penalty for each detected inversion
    if penalties:
        score = max(0.0, 1.0 - 0.3 * penalties)

    return round(score, 2)


def score_cues(steps: list[str]) -> float:
    # Brute force check for cooking cues
    cue_keywords = [
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
    cues_found = any(
        any(cue in step.lower() for cue in cue_keywords) for step in steps
    )
    return 1.0 if cues_found else 0.0


def score_plausibility(steps):
    # Brute force check for implausible instructions
    # assume plausible unless known red flag is found
    instructions = " ".join(steps)
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
    ingredients = recipe_entry["recipe"].split(
        "\n"
    )  # This line remains unchanged
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


def score_conciseness(steps):
    lines = [line for line in steps if line.strip()]
    repeated = sum(1 for i in range(1, len(lines)) if lines[i] == lines[i - 1])
    return round(1 - repeated / len(lines), 2) if lines else 1.0


def score_abed_alignment(recipe_entry, steps, ingredients):
    abeds = recipe_entry.get("input", {})
    if not abeds:
        return 0.0

    score = 0
    total = 0

    # Flatten all relevant recipe text
    text = " ".join(steps + ingredients).lower()

    def match_keywords(keywords, text):
        return any(word in text for word in keywords)

    # Flavor
    for flavor in abeds.get("flavor", []):
        total += 1
        if flavor in FLAVOR_KEYWORDS and match_keywords(
            FLAVOR_KEYWORDS[flavor], text
        ):
            score += 1

    # Texture
    for texture in abeds.get("texture", []):
        total += 1
        if texture in TEXTURE_KEYWORDS and match_keywords(
            TEXTURE_KEYWORDS[texture], text
        ):
            score += 1

    # Type
    if "type" in abeds:
        total += 1
        if abeds["type"].lower() in text:
            score += 1

    return round(score / total, 2) if total else 0.0
