from llama_cpp import Llama

model = Llama(
    model_path='/root/JEDI/jedi_v5_Q4.gguf',
    n_ctx=512, n_threads=8, n_gpu_layers=0, verbose=False,
)

SYS = "You are JEDI - AI engineer. You spawn nanobots as tools."

samples = [
    "How much free RAM?",
    "Write Python to flatten a nested list.",
    "What is a container?",
    "ImportError: No module named flask",
]

for q in samples:
    messages = [{"role": "system", "content": SYS}, {"role": "user", "content": q}]
    out = model.create_chat_completion(messages, max_tokens=256, temperature=0.5)
    text = out['choices'][0]['message']['content']
    print(f"Q: {q}")
    print(f"A: {text}")
    print()
