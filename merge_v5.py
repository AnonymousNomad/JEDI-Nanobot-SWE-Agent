#!/usr/bin/env python3
import os, time
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import torch
torch.set_num_threads(8)

BASE = "/root/.cache/huggingface/hub/models--LiquidAI--LFM2.5-1.2B-Instruct/snapshots/868df74dd56ff8a0c2ac5dbf281690c2dbebe4c9"
ADAPTER = "/root/JEDI/jedi_lora_v5"
OUT = "/root/JEDI/jedi_v5_merged"

from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

tok = AutoTokenizer.from_pretrained(BASE, trust_remote_code=True, local_files_only=True)
print("Loading base...")
base = AutoModelForCausalLM.from_pretrained(
    BASE, dtype=torch.float16, device_map="cpu",
    low_cpu_mem_usage=True, trust_remote_code=True, local_files_only=True,
)
print("Merging v5 adapter...")
model = PeftModel.from_pretrained(base, ADAPTER)
merged = model.merge_and_unload()
merged.save_pretrained(OUT, safe_serialization=True)
tok.save_pretrained(OUT)
size = sum(os.path.getsize(os.path.join(dirpath, f)) for dirpath, _, filenames in os.walk(OUT) for f in filenames)
print(f"Merged model saved: {size/1024**3:.2f}GB")
