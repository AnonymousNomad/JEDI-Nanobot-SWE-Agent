---
language:
- en
license: mit
library_name: transformers
pipeline_tag: text-generation
tags:
- jedi
- cybersecurity
- nanobot
- swarm-intelligence
- vitalis
- lfm
- liquid-foundation-model
- lora
- qlora
- veritas
- machiavelli
- sovereign-ai
- ferrell-synthetic-intelligence
base_model: LiquidAI/LFM2.5-1.2B-Instruct
model_type: liquidfm
inference: true
---

# JEDI — Joint Entity Defense Infrastructure (LFM2.5-1.2B)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Transformers](https://img.shields.io/badge/Transformers-5.x-yellow.svg)](https://huggingface.co/docs/transformers)
[![llama.cpp](https://img.shields.io/badge/llama.cpp-GGUF-green.svg)](https://github.com/ggerganov/llama.cpp)
[![Platform](https://img.shields.io/badge/Platform-ARM64%20%7C%20x86_64-lightgrey.svg)]()
[![GPU](https://img.shields.io/badge/GPU-Optional-brightgreen.svg)]()

**JEDI** is a cybersecurity operations AI built on Liquid AI's `LFM2.5-1.2B-Instruct` architecture, fine-tuned to think like a *mentalist + Machiavelli strategist*. It connects every technical concept to psychology, history, and human nature rather than memorizing facts.

This repo contains the **full project**: training data, generation scripts, the Veritas truth-verification layer, the LoRA fine-tuning pipeline, benchmark runners, and the inference/terminal front-ends.

---

## What This Repo Contains

| Path | What it is |
|------|-----------|
| `training_data_master.jsonl` | **20,847 examples, ~2.67M tokens** — the master fine-tuning dataset (all sources merged) |
| `training_data_connective_v3.jsonl` | 5,763 cross-domain examples (Machiavelli × Technical × Psychology) |
| `training_data_veritas.jsonl` | 723 VERITAS verification examples (self-check, confidence scoring, correction) |
| `self_refine_corrections.jsonl` | 8,999 corrections generated from the test bank |
| `test_10k.jsonl` | 8,999 evaluation questions across 10 domains |
| `generate_connective_v3.py` | Generator for cross-domain training data |
| `generate_veritas.py` | Generator for the Veritas truth layer |
| `generate_10k_test.py` | Generator for the 10K eval bank |
| `self_refine_pipeline.py` | Self-Refine merge/correction pipeline (`merge` / `generate`) |
| `tune_jedi.py` | **LoRA / QLoRA fine-tuning script** (the one to run on your laptop) |
| `eval_benchmarks.py` | Problem-solving / code / reasoning / safety benchmark runner |
| `jedi_terminal.py` | Parrot-OS-styled cyberdeck terminal front-end |
| `jedi_tui.py` / `jedi_chat.py` / `jedi_cortex.py` | Other interaction front-ends |
| `model/LFM2.5-1.2B-Instruct-Q4_K_M.gguf` | The base GGUF model (Q4_K_M, 730 MB) |
| `requirements.txt` | Python dependencies |

---

## Project Status (as of last sync)

| Item | Status |
|------|--------|
| Connective training data generator | ✅ Done (5,763 examples) |
| Veritas truth-verification layer | ✅ Done (723 examples) |
| Master dataset merge | ✅ Done (20,847 examples, 2.67M tokens) |
| 10K eval bank | ✅ Done (8,999 questions) |
| LoRA fine-tuning script | ✅ Written (`tune_jedi.py`) — **NEEDS TO BE RUN** |
| Fine-tuned adapter | ❌ Not yet produced (`jedi_lora_adapter/`) |
| Benchmark numbers post-fine-tune | ❌ Not yet measured |
| Upload to HF | ✅ In progress (this push) |

**Key fact:** No fine-tuning has actually completed yet. The weights in `model/` are still the **base LFM2.5-1.2B-Instruct**. The training data and the script are ready — the run is the missing step.

---

## What Was Done vs. What's Left

### ✅ Completed
1. **Connective training data** — 5,763 examples that tie Machiavelli principles + psychology biases to concrete technical topics (SQLi, XSS, SSRF, IDOR, zero-trust, etc.). Goal was teaching *understanding*, not rote recall.
2. **Veritas layer** — 723 examples teaching the model to self-verify, assign confidence scores (90–100% fact, 70–89% inference, <50% speculation), and correct its own errors.
3. **Self-Refine pipeline** — generates corrected examples from the test bank and merges all sources into `training_data_master.jsonl`.
4. **10K eval bank** — 8,999 questions across recon / exploit / defense / attribution / incident / compliance / psychology / tutor / whiterabbit / software-engineering.
5. **Terminal UI** — Parrot-OS two-line prompt, neon-northern-lights palette, ASCII "JEDI" banner, dynamic status bar, tool panel, White Rabbit Mode animation.

### ⏳ Left To Do (in order)
1. **Run `tune_jedi.py`** to produce `jedi_lora_adapter/` (QLoRA, r=16, ~1 epoch over 20K examples).
2. **Run `eval_benchmarks.py`** on the fine-tuned model to get post-training numbers.
3. **Convert the LoRA adapter to GGUF** (so it can be applied to the GGUF base at inference) — see below.
4. **Optionally re-run all the big public benchmarks** (MMLU / MMLU-Pro / GPQA / IFEval / BFCL) and record the scores.
5. **Apply adapter in the terminal** — load `model/` + LoRA at runtime.

---

## How To Finish It (on your laptop)

### 1. Clone & install
```bash
git lfs install
git clone https://huggingface.co/FerrellSyntheticIntelligence/JEDI
cd JEDI
pip install -r requirements.txt
# If you want LoRA training:
pip install "transformers>=5.2.0" peft bitsandbytes datasets accelerate torch
```

### 2. Run the fine-tune (CPU or GPU)
```bash
# Quick smoke test first (100 examples, 20 steps):
python3 tune_jedi.py --quick

# Full run:
python3 tune_jedi.py
```
This produces `jedi_lora_adapter/` (PEFT LoRA weights). On a laptop GPU this takes minutes; on CPU it can take hours. The script uses 4-bit QLoRA so VRAM/RAM stays low.

### 3. Apply the adapter to the GGUF for inference
Two options:
- **Transformers path:** `python3 tune_jedi.py --apply` loads base + LoRA and tests a generation.
- **GGUF path (recommended for the terminal):** convert the LoRA to a GGUF adapter and load it with `llama_cpp`:
  ```python
  from llama_cpp import Llama
  llm = Llama(model_path="model/LFM2.5-1.2B-Instruct-Q4_K_M.gguf",
              lora_path="jedi_lora_adapter/adapter.bin")  # after conversion
  ```

### 4. Re-benchmark
```bash
python3 eval_benchmarks.py
```
Then compare to the pre-fine-tune baseline in `eval_results.json`.

---

## Data Format

All training files are ShareGPT-style JSONL:
```json
{"messages":[{"role":"system","content":"..."},{"role":"user","content":"..."},{"role":"assistant","content":"..."}],"domain":"machiavelli_psych"}
```
The `tune_jedi.py` script converts this to the LFM2.5 ChatML template (`<|im_start|>...<|im_end|>`) and masks the loss on non-assistant turns.

### Domain distribution in `training_data_master.jsonl`
`cybersec_exploit` (1785), `self_refine_*` (≈7000 across coding/recon/defense/incident/attribution/psych/tutor/whiterabbit), `veritas_*` (723), `machiavelli_psych` (6769), `cybersec_defense` (1154), `cybersec_recon` (254), `whiterabbit` (343), `cybersec_swarm` (247), etc.

---

## Architecture

```
User Input
  → Quadruflow Router (LOGICAL / FACTUAL / CREATIVE / PROCEDURAL)
  → Chain Amplifier (reasoning scaffold)
  → LFM2.5 1.2B Inference (llama-cpp or transformers)
  → VERITAS Loop (self-verify, confidence, correct)
  → Attestation Loop (3-check quality gate)
  → Memory Store (FAISS + Ebbinghaus decay)
  → JEDI Modules (swarm, legal gate, comms, ledger)
  → Response
```

The **Veritas layer** is what's new since the original JEDI release: the model now rates its own confidence and flags speculation instead of presenting guesses as fact.

---

## Intended Use & Ethics
- Built for **authorized defense only** — all operations require legal authorization.
- Immutable audit ledger for every action.
- Built-in safety gate refuses harmful requests.
- Human-in-the-loop required for kinetic actions.

## Citation
```bibtex
@misc{jedi2026,
  title={JEDI: Joint Entity Defense Infrastructure},
  author={Ferrell Synthetic Intelligence},
  year={2026},
  url={https://huggingface.co/FerrellSyntheticIntelligence/JEDI},
  license={MIT}
}
```

## Contact
[Ferrell Synthetic Intelligence](https://huggingface.co/FerrellSyntheticIntelligence) — Neuro_Nomad
