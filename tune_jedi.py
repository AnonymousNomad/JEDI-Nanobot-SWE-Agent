#!/usr/bin/env python3
"""
JEDI_LFM2.5 LoRA Fine-Tuning Script

Trains the model on our cross-domain + Veritas dataset using QLoRA.
Targets: ~2.67M tokens of connective/Machiavelli/Veritas training data.

Usage:
  python3 tune_jedi.py                    # Full training run
  python3 tune_jedi.py --quick            # Quick test run (100 examples)
  python3 tune_jedi.py --resume           # Resume from checkpoint
"""

import json, os, sys, gc, math, random
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
    BitsAndBytesConfig,
    set_seed,
)
from peft import (
    LoraConfig,
    get_peft_model,
    prepare_model_for_kbit_training,
    PeftModel,
)
import bitsandbytes as bnb

# ─── CONFIG ─────────────────────────────────────────────────────
MODEL_ID = "LiquidAI/LFM2.5-1.2B-Instruct"
MASTER_DATA = "/root/JEDI/training_data_master.jsonl"
OUTPUT_DIR = "/root/JEDI/lora_checkpoints"
FINAL_ADAPTER = "/root/JEDI/jedi_lora_adapter"
SEED = 42
set_seed(SEED)

# Training params (CPU-friendly)
LORA_R = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.05
TARGET_MODULES = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
MAX_LENGTH = 1024
BATCH_SIZE = 2          # tiny for CPU
GRAD_ACCUM = 4          # effective batch = 8
LEARNING_RATE = 3e-4
NUM_EPOCHS = 1
WARMUP_STEPS = 50
LOGGING_STEPS = 10
SAVE_STEPS = 200
MAX_STEPS = 1000        # ~2.67M tokens / (1024*8) ≈ 325 steps per epoch, over-estimate

QUICK_MODE = "--quick" in sys.argv
RESUME = "--resume" in sys.argv
if QUICK_MODE:
    MAX_STEPS = 20
    print("[QUICK MODE] Training on 100 examples, 20 steps")


# ─── DATASET ────────────────────────────────────────────────────
class ShareGPTDataset(Dataset):
    """Load ShareGPT-format JSONL and format for causal LM training."""

    def __init__(self, path, tokenizer, max_length=1024, max_examples=None):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.examples = []

        with open(path) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        item = json.loads(line)
                        self.examples.append(item)
                    except json.JSONDecodeError:
                        continue

        if max_examples and len(self.examples) > max_examples:
            random.shuffle(self.examples)
            self.examples = self.examples[:max_examples]

        print(f"Loaded {len(self.examples)} training examples")

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        item = self.examples[idx]
        messages = item.get("messages", [])

        # Format as ChatML (LFM2.5 template)
        formatted = ""
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                formatted += f"<|im_start|>system\n{content}<|im_end|>\n"
            elif role == "user":
                formatted += f"<|im_start|>user\n{content}<|im_end|>\n"
            elif role == "assistant":
                formatted += f"<|im_start|>assistant\n{content}<|im_end|>\n"
        formatted += "<|im_start|>assistant\n"  # prompt for generation

        encoded = self.tokenizer(
            formatted,
            truncation=True,
            max_length=self.max_length,
            padding="max_length",
            return_tensors="pt",
        )

        labels = encoded["input_ids"].clone()
        # Mask user input (don't compute loss on it)
        user_tokens = self.tokenizer(
            "<|im_start|>user\n", add_special_tokens=False
        )["input_ids"]
        assistant_tokens = self.tokenizer(
            "<|im_start|>assistant\n", add_special_tokens=False
        )["input_ids"]

        # Find all user sections and mask their labels
        input_ids = encoded["input_ids"][0]
        labels_seq = labels[0].clone()

        # Simple approach: mask everything before the last assistant token
        # Find positions of assistant tokens
        assistant_len = len(assistant_tokens)
        input_len = len(input_ids)

        # Find last occurrence of assistant header
        last_asst_pos = -1
        for i in range(input_len - assistant_len):
            if (input_ids[i:i+assistant_len] == torch.tensor(assistant_tokens)).all():
                last_asst_pos = i

        if last_asst_pos > 0:
            # Mask everything before the last assistant turn
            labels_seq[:last_asst_pos] = -100
        else:
            # If no assistant found, mask everything (safety)
            labels_seq = torch.full_like(labels_seq, -100)

        return {
            "input_ids": encoded["input_ids"][0],
            "attention_mask": encoded["attention_mask"][0],
            "labels": labels_seq,
        }


# ─── MODEL SETUP ────────────────────────────────────────────────
def setup_model():
    """Load model with QLoRA 4-bit quantization."""
    print(f"Loading model: {MODEL_ID}")

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float32,  # CPU doesn't support bfloat16
    )

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
        dtype=torch.float32,
    )

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    # Prepare for k-bit training
    model = prepare_model_for_kbit_training(model)

    # Configure LoRA
    lora_config = LoraConfig(
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        target_modules=TARGET_MODULES,
        lora_dropout=LORA_DROPOUT,
        bias="none",
        task_type="CAUSAL_LM",
    )

    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    return model, tokenizer


# ─── MAIN ───────────────────────────────────────────────────────
def train():
    model, tokenizer = setup_model()

    max_examples = 100 if QUICK_MODE else None
    dataset = ShareGPTDataset(MASTER_DATA, tokenizer, MAX_LENGTH, max_examples)

    # Data collator
    collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,
    )

    # Training args
    args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=NUM_EPOCHS,
        max_steps=MAX_STEPS,
        per_device_train_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRAD_ACCUM,
        warmup_steps=WARMUP_STEPS,
        logging_steps=LOGGING_STEPS,
        save_steps=SAVE_STEPS,
        learning_rate=LEARNING_RATE,
        lr_scheduler_type="cosine",
        optim="adamw_8bit" if torch.cuda.is_available() else "adamw_torch",
        report_to="none",
        ddp_find_unused_parameters=False,
        gradient_checkpointing=True,
        fp16=False,
        bf16=False,
        dataloader_pin_memory=False,
        max_grad_norm=0.3,
        remove_unused_columns=False,
    )

    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=dataset,
        data_collator=collator,
    )

    # Disable caching
    model.config.use_cache = False

    print(f"\n{'='*50}")
    print(f"Starting training:")
    print(f"  Model: {MODEL_ID}")
    print(f"  Data: {len(dataset)} examples")
    print(f"  Steps: {MAX_STEPS}")
    print(f"  Batch: {BATCH_SIZE} (eff: {BATCH_SIZE * GRAD_ACCUM})")
    print(f"  LoRA r={LORA_R}, α={LORA_ALPHA}")
    print(f"  Device: {'CPU' if not torch.cuda.is_available() else 'GPU'}")
    print(f"{'='*50}\n")

    # Count parameters
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total = sum(p.numel() for p in model.parameters())
    print(f"Trainable params: {trainable:,} / {total:,} ({100*trainable/total:.2f}%)")

    trainer.train(resume_from_checkpoint=RESUME)

    # Save adapter
    model.save_pretrained(FINAL_ADAPTER)
    tokenizer.save_pretrained(FINAL_ADAPTER)
    print(f"\nLoRA adapter saved to: {FINAL_ADAPTER}")

    # Save merged model path for reference
    with open(os.path.join(FINAL_ADAPTER, "base_model.txt"), "w") as f:
        f.write(MODEL_ID)

    print("Training complete!")


def apply_adapter():
    """Apply the trained LoRA adapter back to the base model for testing."""
    print(f"Loading base model + LoRA adapter from {FINAL_ADAPTER}...")
    model = PeftModel.from_pretrained(
        AutoModelForCausalLM.from_pretrained(MODEL_ID, trust_remote_code=True, device_map="auto"),
        FINAL_ADAPTER,
    )
    tokenizer = AutoTokenizer.from_pretrained(FINAL_ADAPTER)

    # Test
    prompt = "<|im_start|>system\nYou are JEDI — forensic analytical engine. Connect everything to psychology and Machiavelli.<|im_end|>\n<|im_start|>user\nWhat is the connection between Machiavelli's 'trust is safer to fear than love' and zero-trust architecture?<|im_end|>\n<|im_start|>assistant\n"

    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(
        **inputs,
        max_new_tokens=200,
        temperature=0.3,
        do_sample=True,
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=False)
    print("\n" + "="*50)
    print("TEST GENERATION:")
    print(response[len(prompt):])
    print("="*50)


if __name__ == "__main__":
    if "--apply" in sys.argv:
        apply_adapter()
    elif "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: python3 tune_jedi.py [--quick|--resume|--apply]")
        print("  (no flag)  Full training run")
        print("  --quick    Quick test (100 examples, 20 steps)")
        print("  --resume   Resume from checkpoint")
        print("  --apply    Test the trained adapter")
    else:
        train()
