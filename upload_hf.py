#!/usr/bin/env python3
"""Upload JEDI project to Hugging Face (FerrellSyntheticIntelligence/JEDI)."""
import os
from huggingface_hub import HfApi

REPO = "FerrellSyntheticIntelligence/JEDI"
BASE = "/root/JEDI"
api = HfApi()

# Files to upload (path, local_path)
uploads = [
    # New README (will replace old)
    ("README.md", os.path.join(BASE, "README_UPLOAD.md")),
    # Training data
    ("training_data_master.jsonl", os.path.join(BASE, "training_data_master.jsonl")),
    ("training_data_connective_v3.jsonl", os.path.join(BASE, "training_data_connective_v3.jsonl")),
    ("training_data_veritas.jsonl", os.path.join(BASE, "training_data_veritas.jsonl")),
    ("self_refine_corrections.jsonl", os.path.join(BASE, "self_refine_corrections.jsonl")),
    ("test_10k.jsonl", os.path.join(BASE, "test_10k.jsonl")),
    # Generation + pipeline scripts
    ("generate_connective_v3.py", os.path.join(BASE, "generate_connective_v3.py")),
    ("generate_veritas.py", os.path.join(BASE, "generate_veritas.py")),
    ("generate_10k_test.py", os.path.join(BASE, "generate_10k_test.py")),
    ("self_refine_pipeline.py", os.path.join(BASE, "self_refine_pipeline.py")),
    ("tune_jedi.py", os.path.join(BASE, "tune_jedi.py")),
    # Benchmarks
    ("eval_benchmarks.py", os.path.join(BASE, "eval_benchmarks.py")),
    ("eval_results.json", os.path.join(BASE, "eval_results.json")),
    ("benchmark_results.json", os.path.join(BASE, "benchmark_results.json")),
    # Original generation scripts (kept for reference)
    ("generate_connective_v2.py", os.path.join(BASE, "generate_connective_v2.py")),
    ("generate_connective_training.py", os.path.join(BASE, "generate_connective_training.py")),
    ("generate_5k.py", os.path.join(BASE, "generate_5k.py")),
    ("generate_5k_v2.py", os.path.join(BASE, "generate_5k_v2.py")),
    ("gen_full_training.py", os.path.join(BASE, "gen_full_training.py")),
    ("_vitalis_loader.py", os.path.join(BASE, "_vitalis_loader.py")),
]

print(f"Uploading {len(uploads)} files to {REPO}...\n")
for repo_path, local_path in uploads:
    if not os.path.exists(local_path):
        print(f"  SKIP (missing): {repo_path}")
        continue
    size = os.path.getsize(local_path)
    print(f"  -> {repo_path} ({size/1024/1024:.1f} MB)")
    api.upload_file(
        path_or_fileobj=local_path,
        path_in_repo=repo_path,
        repo_id=REPO,
        repo_type="model",
    )

print("\nUpload complete.")
