import json
from pathlib import Path
from datetime import datetime, timedelta
from rich.prompt import Prompt
from rich.console import Console

console = Console()


# NOTE:
# This function only loads the single most recent
# reviews.jsonl from the past 7 days.
# In the future, this may be expanded to aggregate
# reviews across multiple dates.
def find_latest_reviews_file():
    base = Path("logs")
    if not base.exists():
        console.print("[red]No logs directory found.")
        return None

    # Walk backwards by date
    for days_back in range(0, 7):
        date = datetime.now().date() - timedelta(days=days_back)
        log_path = (
            base
            / str(date.year)
            / f"{date.month:02d}"
            / f"{date.day:02d}"
            / "reviews.jsonl"
        )
        if log_path.exists():
            return log_path
    return None


def load_reviews(path):
    with open(path, "r") as f:
        return [json.loads(line.strip()) for line in f if line.strip()]


def save_rating(entry, score):
    rating_path = Path(entry["_review_path"]).with_name("ratings.jsonl")
    log_data = {
        "title": entry["title"],
        "abed_input": entry["abed_input"],
        "RScore": entry["RScore"],
        "human_rating": score,
        "timestamp": datetime.now().isoformat(),
    }
    with open(rating_path, "a") as f:
        f.write(json.dumps(log_data) + "\n")


def load_existing_ratings(rating_path):
    if not rating_path.exists():
        return set()
    with open(rating_path, "r") as f:
        return {json.loads(line)["title"] for line in f if line.strip()}


def review():
    latest = find_latest_reviews_file()
    if not latest:
        console.print("[red]No reviews.jsonl file found in recent logs.")
        return

    reviews = load_reviews(latest)
    rating_path = latest.with_name("ratings.jsonl")
    reviewed_titles = load_existing_ratings(rating_path)

    console.print(f"[green]Loaded {len(reviews)} reviews from {latest}")
    num_reviewed = 0
    for entry in reviews:
        if entry["title"] in reviewed_titles:
            continue
        num_reviewed += 1
        console.rule(entry["title"])
        console.print(f"ABED: {entry['abed_input']}")
        console.print(f"Model Score: {entry['RScore']}")
        entry["_review_path"] = latest
        score = Prompt.ask(
            "Your rating (1–5, or enter to skip)",
            default="",
            show_default=False,
        )
        if score.strip() == "":
            continue
        try:
            score = float(score)
            if 1 <= score <= 5:
                normalized_score = round((score - 1) / 4, 2)
                save_rating(entry, normalized_score)
                console.print("[cyan]✔ Saved\n")
            else:
                console.print("[red]Invalid score. Must be between 1 and 5.")
        except ValueError:
            console.print("[red]Invalid input. Must be a number.")

    if num_reviewed > 0:
        console.print(f"[green]Reviewed {num_reviewed} recipes")
    else:
        console.print("[red]No new reviews to save.")


if __name__ == "__main__":
    review()
