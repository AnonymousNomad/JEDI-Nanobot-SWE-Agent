from llama_cpp import Llama

model = Llama(
    model_path='/root/JEDI/jedi_v4_Q4.gguf',
    n_ctx=512,
    n_threads=8,
    n_gpu_layers=0,
    verbose=False,
)

tests = [
    'How much free RAM?',
    'Write Python to flatten a nested list.',
    'What is a container?',
    'Explain TCP vs UDP.',
    'ImportError: No module named flask',
]

for q in tests:
    messages = [
        {'role': 'system', 'content': 'You are JEDI - AI engineer. You spawn nanobots as tools.'},
        {'role': 'user', 'content': q},
    ]
    out = model.create_chat_completion(messages, max_tokens=256, temperature=0.5)
    text = out['choices'][0]['message']['content']
    spawn = '[Spawn:' in text
    conclusion = '[Conclusion]' in text
    code = '```' in text
    print(f'Q: {q[:50]}')
    print(f'A: {text[:200]}')
    print(f'  Spawn={spawn} Conc={conclusion} Code={code}')
    print()
