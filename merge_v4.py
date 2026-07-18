#!/usr/bin/env python3
import os, sys, json, time, gc
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import torch
torch.set_num_threads(8)

BASE_MODEL = "/root/.cache/huggingface/hub/models--LiquidAI--LFM2.5-1.2B-Instruct/snapshots/868df74dd56ff8a0c2ac5dbf281690c2dbebe4c9"
ADAPTER_PATH = "/root/JEDI/jedi_lora_v4"
MERGED_PATH = "/root/JEDI/jedi_v4_merged"

from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

tok = AutoTokenizer.from_pretrained(BASE_MODEL, trust_remote_code=True, local_files_only=True)
print(f"Loading base model...")
t0 = time.time()
base = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    dtype=torch.float16,
    device_map="cpu",
    low_cpu_mem_usage=True,
    trust_remote_code=True,
    local_files_only=True,
)
print(f"Base loaded in {time.time()-t0:.0f}s")

print("Loading and merging LoRA...")
t0 = time.time()
model = PeftModel.from_pretrained(base, ADAPTER_PATH)
merged = model.merge_and_unload()
print(f"Merge done in {time.time()-t0:.0f}s")

merged.save_pretrained(MERGED_PATH, safe_serialization=True)
tok.save_pretrained(MERGED_PATH)
print(f"Merged model saved to {MERGED_PATH}")
print(f"Size: {sum(os.path.getsize(os.path.join(dirpath, f)) for dirpath, _, filenames in os.walk(MERGED_PATH) for f in filenames) / 1024**3:.2f}GB")
