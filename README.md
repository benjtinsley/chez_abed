# Chez Abed

**Chez Abed** is a kitchen for an LLM-powered recipe generation tool. Instead of providing a list of ingredients, users input abstract sensory descriptors—called **ABEDs** (Abstracted Bare Element Descriptors) such as flavors, textures, and meal type. Chez Abed transforms these inputs into complete recipes and scores them based on creativity, structure, and coherence.

---

## 🍽️ What It Does

- Accepts abstract descriptors for:
  - **Flavor** (e.g., sour, sweet, bitter)
  - **Texture** (e.g., crispy, smooth, chewy)
  - **Type** (e.g., Dinner, Snack, Dessert)
- Generates full ingredient lists and cooking instructions
- Scores each recipe across multiple qualitative and quantitative metrics
- Stores recipe data and scores for later inspection

---

## 🧪 Phase 1: Test Kitchen

The current implementation is a **proof of concept**, emphasizing:
- Prompting workflows
- Basic scoring heuristics
- ABED vocabulary architecture
- CLI interface for structured generation + evaluation

Under the hood it uses the OpenAI GPT-3.5 Turbo model, so an OpenAI API key is needed to it.

---

## 🚀 Getting Started

1. **Install dependencies**

   We recommend using a virtual environment.

   ```bash
   $ python -m venv .venv && source .venv/bin/activate 
   ```

   Install the dependencies.

   ```bash
   $ pip install -r requirements.txt
   ```

2. **Set your OpenAI API key**

   Create a `.env` file:

   ```
   $ mv .env.example .env
   ```

    In the newly created `.env` file, add your [OpenAI API key](https://platform.openai.com/api-keys):
   ```env
   OPENAI_API_KEY=your_key_here
   ```

3. **Run the interactive menu**

   ```bash
   python -m app.scripts.menu
   ```

   You'll be guided to select ABEDs for one or more recipes. The tool will then:
   - Generate recipes using `generate.py`
   - Score them using `evaluate.py`

   Generated recipes will be stored at logs/[year]/[month]/[date]/[time]-[recipe-title].md
---

## 🗃️ File Structure

```
chez_abed/
├── app/
|   ├── data/
|   │   ├── abed_vocab.json                    # ABED categories and descriptor options
|   │   ├── generated_abed_prompts.json        # Input prompts collected during CLI run
|   │   ├── generated_recipes.json             # Output from recipe generation
|   │   └── generated_scored_recipes.json      # Scored results of recipes
|   ├── evaluation/
|   │   └── scoring.py                         # Scoring logic
|   ├── scripts/
|   │   ├── generate.py                        # Calls OpenAI to generate recipes
|   │   ├── evaluate.py                        # Evaluates and scores generated recipes
|   │   └── menu.py                            # Interactive CLI for creating recipe prompts
├── logs/                                      # Logged recipes
├── metrics_config.yaml                        # Scoring weights and novelty thresholds
├── .env                                       # OpenAI key & other environment variables (not checked in)
├── requirements.txt
└── README.md
```

---

## 📊 Scoring Metrics

Each recipe is scored based on a weighted composite called `MScore`, considering:

- Ingredient usage completeness
- Instruction coherence
- Conciseness
- Plausibility
- Cue richness
- Novelty

Future versions will include more NLP-driven and LLM-reflective scoring.

---

## 🧠 Future Plans

- Incorporate additional ABEDs like mood, technique, diet
- Replace heuristic scoring with NLP/embedding-based comparisons
- Build and fine-tune a standalone LLM using Hugging Face models and domain-specific culinary datasets
- Use OpenAI generations and Phase 1 scoring to guide dataset construction for training
- Add markdown export, visualizations, and recipe summaries

---

## 🍷 License

Apache 2.0 License. Use responsibly and creatively (not legally binding, just good advice).
