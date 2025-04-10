# config.py – shared configuration for Chez Abed

from pathlib import Path

# Base directory
ROOT_DIR = Path(__file__).resolve().parent

# Common paths
DATA_DIR = ROOT_DIR / "data"
LOGS_DIR = ROOT_DIR / "logs"
PROMPTS_DIR = ROOT_DIR / "prompts"
APP_DIR = ROOT_DIR / "app"

# Files
VOCAB_FILE = DATA_DIR / "abed_vocab.json"
PROMPTS_FILE = DATA_DIR / "generated_abed_prompts.json"
GENERATED_RECIPES_FILE = DATA_DIR / "generated_recipes.json"
GENERATED_SCORED_RECIPES_FILE = DATA_DIR / "generated_scored_recipes.json"
SCORED_RECIPES_FILE = DATA_DIR / "scored_recipes.json"
METRICS_CONFIG_FILE = APP_DIR / "evaluation" / "metrics_config.yaml"
TEMPLATE_PROMPT_FILE = PROMPTS_DIR / "base_prompt_template.txt"
GENERATIONS_LOG_FILE = LOGS_DIR / "generations_log.csv"

# LLM configuration
DEFAULT_MODEL = "gpt-3.5-turbo"  # gpt-3.5-turbo, gpt-4 are the best to use.
TEMPERATURE = 1.0  # 0.0 = deterministic, 1.0 = more random
MAX_TOKENS = 800

# App options
DEBUG = False
