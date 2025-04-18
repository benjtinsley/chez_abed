import re
import yaml
import csv
from datetime import datetime
import json
from pathlib import Path
from config import METRICS_CONFIG_FILE, GENERATIONS_LOG_FILE
from sentence_transformers import SentenceTransformer, util
import pickle

EMBEDDING_CACHE_PATH = Path("logs") / "embeddings_cache.pkl"
if EMBEDDING_CACHE_PATH.exists():
    with open(EMBEDDING_CACHE_PATH, "rb") as f:
        EMBEDDING_CACHE = pickle.load(f)
else:
    EMBEDDING_CACHE = {}

EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")

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


def score_recipe(
    recipe_entry, parsed_steps, parsed_ingredients, log_reviews=False
):
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
        "redundancy_clarity": score_redundancy_clarity(parsed_steps),
        "abed_alignment": score_abed_alignment(
            recipe_entry, parsed_steps, parsed_ingredients
        ),
    }

    # Weights for each metric
    weights = METRICS_CONFIG_FILE["weights"]

    total = sum(scores[k] * weights.get(k, 0) for k in scores)
    scores["RScore"] = round(total, 4)

    if log_reviews:
        title_line = (
            recipe_entry["recipe"]
            .split("**Title:**")[1]
            .split("\n")[0]
            .strip()
        )
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "title": title_line,
            "abed_input": recipe_entry.get("input", {}),
            "RScore": scores["RScore"],
        }

        today = datetime.now()
        log_path = (
            Path("logs")
            / str(today.year)
            / f"{today.month:02d}"
            / f"{today.day:02d}"
            / "reviews.jsonl"
        )
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

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
    ingredients = recipe_entry["recipe"].split("\n")
    ingredient_text = ", ".join(
        extract_ingredient_name(ing) for ing in ingredients if ing.strip()
    )
    current_text = f"{title}. Ingredients: {ingredient_text}"
    if title in EMBEDDING_CACHE:
        current_embedding = EMBEDDING_CACHE[title]
    else:
        current_embedding = EMBEDDING_MODEL.encode(
            current_text, convert_to_tensor=True
        )
        EMBEDDING_CACHE[title] = current_embedding
        with open(EMBEDDING_CACHE_PATH, "wb") as f:
            pickle.dump(EMBEDDING_CACHE, f)

    similarities = []
    if log_path.exists():
        with open(log_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                past_text = (
                    f"{row['title']}. Ingredients: {row['ingredients']}"
                )
                if row["title"] in EMBEDDING_CACHE:
                    past_embedding = EMBEDDING_CACHE[row["title"]]
                else:
                    past_embedding = EMBEDDING_MODEL.encode(
                        past_text, convert_to_tensor=True
                    )
                    EMBEDDING_CACHE[row["title"]] = past_embedding
                    with open(EMBEDDING_CACHE_PATH, "wb") as f:
                        pickle.dump(EMBEDDING_CACHE, f)
                sim = util.pytorch_cos_sim(
                    current_embedding, past_embedding
                ).item()
                similarities.append(sim)

    max_sim = max(similarities, default=0)
    novelty_score = 1.0 - max_sim

    with open(log_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["title", "ingredients"])
        writer.writerow(
            {
                "title": title,
                "ingredients": ingredient_text,
            }
        )

    return round(novelty_score, 2)


def score_conciseness(steps):
    lines = [line for line in steps if line.strip()]
    repeated = sum(1 for i in range(1, len(lines)) if lines[i] == lines[i - 1])
    return round(1 - repeated / len(lines), 2) if lines else 1.0


def match_keywords(keywords, text):
    return any(word in text for word in keywords)


def score_abed_alignment(recipe_entry, steps, ingredients):
    abeds = recipe_entry.get("input", {})

    if not abeds:
        return 0.0

    score = 0
    total = 0

    # Flatten all relevant recipe text
    text = " ".join(steps + ingredients).lower()

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


def score_redundancy_clarity(steps):
    repeated_lines = 0
    seen_steps = set()
    for step in steps:
        clean = step.strip().lower()
        if clean in seen_steps:
            repeated_lines += 1
        seen_steps.add(clean)

    implausible_orderings = [
        ("serve", "cook"),
        ("serve", "bake"),
        ("garnish", "fry"),
        ("garnish", "roast"),
    ]
    order_issues = 0
    for a, b in implausible_orderings:
        idx_a = idx_b = -1
        for i, step in enumerate(steps):
            s = step.lower()
            if a in s and idx_a == -1:
                idx_a = i
            if b in s and idx_b == -1:
                idx_b = i
        if idx_a != -1 and idx_b != -1 and idx_a < idx_b:
            order_issues += 1

    penalty = (repeated_lines + order_issues) * 0.2
    score = max(0.0, 1.0 - penalty)
    return round(score, 2)
