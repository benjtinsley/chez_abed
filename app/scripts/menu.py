import json
import subprocess
import questionary
from rich.console import Console
from config import PROMPTS_FILE, VOCAB_FILE

console = Console()


def load_abed_vocab():
    with open(VOCAB_FILE, "r") as f:
        return json.load(f)


def collect_abed_input(abed_vocab):
    prompt = {}

    for item in abed_vocab:
        prompt_type = "checkbox" if item["multi"] else "select"
        answer = getattr(questionary, prompt_type)(
            message=item["prompt"],
            instruction=item["instruction"],
            choices=item["options"],
        ).ask()

        if item["required"] and not answer:
            print(
                f"⚠️  {item['name'].capitalize()} is required. Please select "
                "at least one."
            )
            return collect_abed_input(abed_vocab)

        prompt[item["name"]] = answer

    return prompt


def main():
    print(
        "🍳 Welcome to Chez Abed: Recipe creation from "
        "Abstracted Bare Element Descriptors.\n"
    )

    abed_vocab = load_abed_vocab()
    all_prompts = []

    while True:
        abed_set = collect_abed_input(abed_vocab)
        all_prompts.append(abed_set)

        more = questionary.confirm(
            "Would you like to add another recipe?", default=False
        ).ask()
        if not more:
            break

    # Show summary
    print(
        "\n📃 Preparing to generate",
        len(all_prompts),
        "recipe(s) with the following profiles:\n",
    )
    for idx, prompt in enumerate(all_prompts, start=1):
        flavor = ", ".join(prompt["flavor"]) if prompt["flavor"] else "—"
        texture = ", ".join(prompt["texture"]) if prompt["texture"] else "—"
        dietary_restrictions = (
            ", ".join(prompt["dietary_restrictions"])
            if prompt["dietary_restrictions"]
            else "—"
        )

        console.print(f"[bold][magenta]{idx}.[/magenta]")
        console.print(
            f"   [bold underline]{prompt['mood']}"
            f" {prompt['type']} for {prompt['total_served']}[/]"
        )
        console.print(
            f"   [green bold]Flavor:[/] {flavor} |"
            f" [green bold]Texture:[/] {texture}"
        )
        console.print(f"   [green bold]Diet:[/] {dietary_restrictions}")
        console.print(
            f"   [green bold]Technique Level:[/] {prompt['technique_level']} |"
            f" [green bold]Prep Time:[/] {prompt['prep_time']}"
        )

    # Save to prompts file
    with open(PROMPTS_FILE, "w") as f:
        json.dump(all_prompts, f, indent=2)

    print("\n👆 Generating recipes...")
    subprocess.run(["python", "-m", "app.scripts.generate"])

    print("✏️ Scoring recipes...")
    subprocess.run(["python", "-m", "app.scripts.evaluate"])

    print("\n✅ All recipes generated and scored!\nCheck your files:")
    print("- 🧾 data/generated_recipes.json")
    print("- 🏆 data/generated_scored_recipes.json")


if __name__ == "__main__":
    main()
