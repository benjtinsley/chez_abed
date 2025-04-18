import json
from pathlib import Path
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    Trainer,
    TrainingArguments,
    DataCollatorForLanguageModeling,
)
import torch

# Model Config
MODEL_NAME = "distilgpt2"
DATA_PATH = Path(__file__).parent / "data" / "abed_recipes.jsonl"
MAX_LENGTH = 512
OUTPUT_DIR = "models/chez-abed-gpt2"


# Load + Prepare Data
def flatten_abed(abed):
    parts = []
    if abed["flavor"]:
        parts.append("flavor=" + ",".join(abed["flavor"]))
    if abed["texture"]:
        parts.append("texture=" + ",".join(abed["texture"]))
    if abed["type"]:
        parts.append("type=" + abed["type"])
    return " | ".join(parts)


def flatten_recipe(output):
    return (
        output.get("title", "")
        + "\n"
        + "\n".join(output.get("ingredients", []))
        + "\n"
        + "\n".join(output.get("steps", []))
    )


def load_dataset(path):
    samples = []
    with open(path) as f:
        for line in f:
            item = json.loads(line)
            abed_str = flatten_abed(item["input"])
            recipe_str = flatten_recipe(item["output"])
            samples.append({"text": abed_str + "\n" + recipe_str})
    return Dataset.from_list(samples)


# Load Model + Tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
tokenizer.pad_token = tokenizer.eos_token  # for GPT-2 compatibility

model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

if torch.cuda.is_available():
    device = torch.device("cuda")
elif torch.backends.mps.is_available():
    device = torch.device("mps")
else:
    device = torch.device("cpu")

print(f"🧠 Using device: {device}")
model.to(device)

# Tokenize Dataset
dataset = load_dataset(DATA_PATH)


def tokenize(batch):
    return tokenizer(
        batch["text"],
        truncation=True,
        padding="max_length",
        max_length=MAX_LENGTH,
    )


tokenized = dataset.map(tokenize, batched=True)

# Training
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=4,
    num_train_epochs=3,
    logging_steps=10,
    save_steps=200,
    save_total_limit=2,
    eval_strategy="no",
    fp16=torch.cuda.is_available(),
    dataloader_pin_memory=True,
    gradient_accumulation_steps=2,
    report_to="none",
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized,
    data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
)

trainer.train()
trainer.save_model(OUTPUT_DIR)
print(f"✅ Model saved to {OUTPUT_DIR}")
