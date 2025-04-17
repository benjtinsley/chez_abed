# Chez Abed

**Chez Abed** is a kitchen for an LLM-powered recipe generation tool. Instead of providing a list of ingredients, users input **ABED**s (Abstracted Bare Element Descriptors) such as flavors, textures, and meal type. Chez Abed transforms these inputs into complete recipes and scores them based on creativity, structure, and coherence.

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

4. **Review recipes**

   ```bash
   python -m app.scripts.review
   ```

   You'll be prompted to rate each recipe on a scale of 1 to 5, which will be used to fine-tune the scoring model to your preferences.

   The reviewable recipes will be stored at `logs/[year]/[month]/[date]/reviews.jsonl`

   Any recipes reviewed will be stored at `logs/[year]/[month]/[date]/ratings.jsonl`

---


## Example Recipes

### Dinner
Given `Flavor: sour, peppery, sweet, fatty, salty | Texture: juicy, smooth, soft, tender, chewy | Type: Dinner`, Chez Abed generates:

```md
**Title:** Sweet and Sour Peppered Pork Stir-Fry

**Description:** This flavorful and comforting stir-fry combines the tangy sourness of vinegar, the heat of black pepper, a touch of sweetness, and the richness of pork. The juicy bell peppers and tender pork pieces create a satisfying texture that pairs perfectly with steamed rice for a delicious dinner.

**Equipment:**
- Wok or large skillet
- Wooden spoon
- Knife
- Cutting board

**Ingredients:**
- 1 lb pork tenderloin, sliced into thin strips
- 2 bell peppers (assorted colors), thinly sliced
- 3 cloves garlic, minced
- 1 onion, thinly sliced
- 1/4 cup soy sauce
- 2 tablespoons rice vinegar
- 2 tablespoons honey
- 1 tablespoon black pepper
- 1 tablespoon cornstarch
- 2 tablespoons vegetable oil
- Salt, to taste
- Cooked rice, for serving

**Instructions:**
1. In a small bowl, mix the soy sauce, rice vinegar, honey, and black pepper. Set aside.
2. Heat vegetable oil in a wok over medium-high heat. Add the sliced pork and stir-fry until browned and cooked through.
3. Remove the pork from the wok and set aside. In the same wok, add more oil if needed and sauté the garlic and onion until fragrant.
4. Add the sliced bell peppers to the wok and stir-fry until they start to soften but remain juicy.
5. Return the cooked pork to the wok. Pour the soy sauce mixture over the pork and veggies.
6. In a small bowl, mix the cornstarch with a little water to create a slurry. Pour the slurry into the wok, stirring continuously until the sauce thickens.
7. Season with salt to taste. Continue to cook for another minute to allow the flavors to meld together.
8. Serve the sweet and sour peppered pork stir-fry over steamed rice.

**Tags:** flavor=sweet, sour, peppery, salty | texture=juicy, tender | type=Dinner

---

**MScore:** 0.91
- Ingredient_usage_completeness: ✅
- Instruction_coherence: ✅
- Cues: ✅
- Plausibility: ✅
- Novelty: ✅
- Conciseness: ✅
```

### Dessert
Given `Flavor: sweet, spiced, earthy, bitter | Texture: crispy, juicy, creamy, fluffy | Type: Dessert`, Chez Abed generates:

```md
**Title:** Spiced Pumpkin Bread Pudding

**Description:** Indulge in a comforting and aromatic dessert experience with this spiced pumpkin bread pudding. The sweet and earthy flavors of pumpkin blend harmoniously with warm spices, creating a cozy and satisfying treat. The crispy top layer contrasts beautifully with the creamy and fluffy interior, making each bite a delightful texture adventure.

**Equipment:**
- Mixing bowl
- Whisk
- Baking dish
- Saucepan

**Ingredients:**
- 4 cups cubed day-old bread (such as brioche or challah)
- 1 can (15 oz) pumpkin puree
- 1 cup heavy cream
- 1 cup milk
- 3/4 cup brown sugar
- 3 eggs
- 1 tsp vanilla extract
- 1 tsp ground cinnamon
- 1/2 tsp ground nutmeg
- 1/2 tsp ground ginger
- 1/4 tsp ground cloves
- 1/4 tsp salt
- 1/4 cup chopped pecans (optional)
- Whipped cream, for serving

**Instructions:**
1. Preheat the oven to 350°F (180°C) and grease a baking dish.
2. In a mixing bowl, whisk together the pumpkin puree, heavy cream, milk, brown sugar, eggs, vanilla extract, spices, and salt until well combined.
3. Add the cubed bread to the pumpkin mixture and gently fold until the bread is coated evenly. Let it sit for 10-15 minutes to allow the bread to soak up the liquid.
4. Pour the mixture into the prepared baking dish, spreading it out evenly. Sprinkle chopped pecans on top if using.
5. Bake in the preheated oven for 40-45 minutes or until the top is golden and the pudding is set.
6. Serve warm, topped with a dollop of whipped cream. Enjoy the creamy and fluffy interior with a crispy top layer, filled with sweet, spiced, and earthy flavors.

**Tags:** flavor=[sweet, spiced, earthy, bitter] | texture=[crispy, creamy, fluffy] | type=[Dessert]

---

**MScore:** 0.83
- Ingredient_usage_completeness: ✅
- Instruction_coherence: ✅
- Cues: ✅
- Plausibility: ✅
- Novelty: ✅
- Conciseness: ✅
```

### Breakfast
Given `Flavor: peppery, salty, earthy | Texture: crispy, tender, fluffy, grainy | Type: Breakfast`, Chez Abed generates:

```md
**Title:** Crunchy Quinoa Breakfast Bowl

**Description:** Start your day with a flavorful and nutritious breakfast bowl that combines the peppery, salty, and earthy notes of quinoa with a variety of textures. The crispy quinoa contrasts beautifully with the tender avocado and fluffy scrambled eggs, creating a satisfying and energizing meal to kickstart your morning.

**Equipment:**
- Medium saucepan
- Skillet
- Mixing bowl

**Ingredients:**
- 1/2 cup quinoa
- 1 cup water
- 2 eggs
- 1 avocado, diced
- 1/4 cup cherry tomatoes, halved
- 1/4 cup feta cheese, crumbled
- 1/4 teaspoon black pepper
- 1/4 teaspoon salt
- 1 tablespoon olive oil

**Instructions:**
1. Rinse the quinoa under cold water using a fine-mesh strainer.
2. In a medium saucepan, combine the rinsed quinoa and water. Bring to a boil, then reduce heat to low, cover, and simmer for 15-20 minutes until the quinoa is fluffy and tender.
3. In a skillet, heat olive oil over medium heat.
4. Crack the eggs into a mixing bowl, season with salt and pepper, and whisk until well combined.
5. Pour the eggs into the skillet and scramble until cooked through. Remove from heat.
6. Divide the cooked quinoa into bowls.
7. Top the quinoa with scrambled eggs, diced avocado, cherry tomatoes, and crumbled feta cheese.
8. Sprinkle with a pinch of black pepper for an extra peppery kick.
9. Serve the crunchy quinoa breakfast bowl hot and enjoy the mix of flavors and textures!

**Tags:** flavor=[peppery, salty, earthy] | texture=[crispy, tender, fluffy] | type=[Breakfast]

---

**MScore:** 0.92
- Ingredient_usage_completeness: ✅
- Instruction_coherence: ✅
- Cues: ✅
- Plausibility: ✅
- Novelty: ✅
- Conciseness: ✅
```

## 🗃️ File Structure

```
chez_abed/
├── app/
│  ├── evaluation/
│  │   ├── metrics_config.yaml                # Scoring weights and novelty thresholds
│  │   └── scoring.py                         # Scoring logic
│  ├── scripts/
│  │   ├── generate.py                        # Calls OpenAI to generate recipes
│  │   ├── evaluate.py                        # Evaluates and scores generated recipes
│  │   └── menu.py                            # Interactive CLI for creating recipe prompts
│  ├── utils/
│  │   └── logging.py                         # Formats generated recipes to log/ format
├── data/
│   ├── abed_vocab.json                       # ABED categories and descriptor options
│   ├── generated_abed_prompts.json           # Input prompts collected during CLI run
│   ├── generated_recipes.json                # Output from recipe generation
│   └── generated_scored_recipes.json         # Scored results of recipes
├── logs/                                     # Logged recipes
├── prompts/                                  # Prompts to generate consistent recipes
├── .env                                      # OpenAI key & other environment variables (not checked in)
├── README.md
└── requirements.txt
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

- [x] Incorporate additional ABEDs like mood, technique, diet
- [x] Replace heuristic scoring with NLP/embedding-based comparisons
- [ ] Build and fine-tune a standalone LLM using Hugging Face models and domain-specific culinary datasets
- [ ] Use OpenAI generations and Phase 1 scoring to guide dataset construction for training
- [ ] Add markdown export, visualizations, and recipe summaries

---

## 🍷 License

Apache 2.0 License. Use responsibly and creatively (not legally binding, just good advice).
