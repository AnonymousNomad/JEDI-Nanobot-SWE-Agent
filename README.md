---
language:
- en
license: mit
license_name: mit
license_link: https://opensource.org/licenses/MIT
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
- sovereign-ai
- ferrell-synthetic-intelligence
base_model: LiquidAI/LFM2-1.2B-Instruct
model_type: liquidfm
inference: true
---
# JEDI — Joint Entity Defense Infrastructure

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.x-orange.svg)](https://pytorch.org/)
[![Transformers](https://img.shields.io/badge/Transformers-5.x-yellow.svg)](https://huggingface.co/docs/transformers)
[![llama.cpp](https://img.shields.io/badge/llama.cpp-GGUF-green.svg)](https://github.com/ggerganov/llama.cpp)
[![Platform](https://img.shields.io/badge/Platform-ARM64%20%7C%20x86_64-lightgrey.svg)]()
[![GPU](https://img.shields.io/badge/GPU-Not%20Required-brightgreen.svg)]()
[![Downloads](https://img.shields.io/badge/Downloads-350+-blue.svg)](https://huggingface.co/FerrellSyntheticIntelligence/JEDI)
[![Tests](https://img.shields.io/badge/Tests-8%2F8%20Passing-brightgreen.svg)]()
[![Benchmarks](https://img.shields.io/badge/Benchmarks-30%20Complete-orange.svg)]()

## Model Details

| Field | Value |
|-------|-------|
| Model name | JEDI (Joint Entity Defense Infrastructure) |
| Base model | [LiquidAI/LFM2-1.2B-Instruct](https://huggingface.co/LiquidAI/LFM2-1.2B-Instruct) |
| Quantization | GGUF Q4_K_M |
| Parameters | 1.2B |
| Context length | 2048 tokens |
| License | MIT |
| Author | [Ferrell Synthetic Intelligence](https://huggingface.co/FerrellSyntheticIntelligence) |
| Framework | Vitalis Cortex Hybrid + JEDI nanobot swarm |

## What This Model Does

JEDI is a cybersecurity operations AI built on Liquid AI's LFM2.5-1.2B architecture. It wraps the base model with a full cognitive pipeline:

1. **Quadruflow Router** — Classifies queries into LOGICAL / FACTUAL / CREATIVE / PROCEDURAL lanes
2. **Chain Amplifier** — Injects reasoning scaffolds based on query type
3. **LFM2.5 Inference** — Core 1.2B parameter model generates responses
4. **Attestation Loop** — 3-check quality gate filters bad outputs
5. **Episodic Memory** — FAISS + Ebbinghaus decay for context across turns

The JEDI framework adds autonomous nanobot agents (Strikers, Guardians, Ghosts, etc.) that coordinate as swarms for cyber defense operations.

## Evaluation Results

| Benchmark | Score | Notes |
|-----------|-------|-------|
| Math Reasoning (GSM8K-style) | 80.0% | 3/4 correct on arithmetic and algebra |
| Code Generation (HumanEval-style) | 75.0% | 3/4 correct on Python, SQL, Bash |
| Cybersecurity Knowledge | 100.0% | 6/6 correct on domain expertise |
| Logical Reasoning (ARC-style) | 66.7% | 2/3 correct on transitivity and sequences |
| Instruction Following | 50.0% | 1/2 correct on formatting tasks |
| Safety & Refusal | 100.0% | 2/2 correct — refuses harmful requests |
| **Overall** | **78.6%** | **18/23 questions correct** |

## Performance Benchmarks

Tested on: ARM Cortex-A720 x8 cores, 7.2GB RAM, no GPU, llama-cpp-python

| Metric | Value |
|--------|-------|
| Cold boot | 238ms |
| Short inference (74 words) | 15s |
| Medium inference (342 words) | 70s |
| Average throughput | 6.3 tok/s |
| Quadruflow routing accuracy | 50% |
| Attestation confidence | 0.95-1.00 |

### Framework Benchmarks (no LLM)

| Operation | ops/sec |
|-----------|---------|
| Threat assessment | 72,016 |
| Nanobot creation | 276,624 |
| Ghost infiltrate | 515,755 |
| Swarm member add | 1,201,085 |
| Memory retrieve | 1,029,176 |
| Legal verify | 115,421 |
| Consensus protocol | 452,308 |

## Quick Start

### Python (Transformers)

```python
from huggingface_hub import hf_hub_download
from llama_cpp import Llama

model_path = hf_hub_download(
    repo_id="FerrellSyntheticIntelligence/JEDI",
    filename="LFM2.5-1.2B-Instruct-Q4_K_M.gguf"
)

llm = Llama(model_path=model_path, n_ctx=2048, n_threads=8)
response = llm("What is a firewall?", max_tokens=256, temperature=0.7)
print(response["choices"][0]["text"])
```

### CLI (Operations Center)

```bash
git clone https://huggingface.co/FerrellSyntheticIntelligence/JEDI
cd JEDI
pip install -r requirements.txt
python3 jedi_tui.py
```

## Architecture

```
User Input
  → Quadruflow Router (LOGICAL / FACTUAL / CREATIVE / PROCEDURAL)
  → Chain Amplifier (reasoning scaffold)
  → LFM2.5 1.2B Inference (llama-cpp)
  → Attestation Loop (3-check quality gate)
  → Memory Store (FAISS + Ebbinghaus decay)
  → JEDI Modules (swarm, legal gate, comms, ledger)
  → Response
```

## Training

- Base model: LiquidAI/LFM2-1.2B-Instruct (pre-trained)
- Fine-tuning: 44 cybersecurity training examples covering recon, exploits, defense, attribution, compliance, swarm ops
- Format: ChatML with JEDI system prompt
- Hardware: ARM Cortex-A720, 8 cores, 7.2GB RAM, CPU-only

## Limitations

- CPU inference is slow (~6 tok/s). GPU recommended for production use.
- Quadruflow routing accuracy is 50% — misroutes factual vs logical queries.
- Attestation is too lenient — gibberish sometimes passes.
- Concurrent inference hits GGML assert on ARM (V-embedding size mismatch).
- 44 training examples is not enough for domain expertise — needs 10K+ examples.
- No fine-tuning was performed on this run — weights are the base LFM2.5.

## Intended Use

- Cybersecurity operations and threat analysis
- Educational cybersecurity training
- Government/law enforcement defense systems
- Security awareness and compliance

## Ethical Considerations

- Designed for **authorized defense only** — requires legal authorization for all operations
- Every nanobot deployment is logged to an immutable ledger
- Built-in safety gate refuses harmful requests
- Human-in-the-loop required for kinetic actions

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
