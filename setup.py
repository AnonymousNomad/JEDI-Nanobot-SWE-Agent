from setuptools import setup, find_packages

setup(
    name="jedi",
    version="0.1.0",
    description="Joint Entity Defense Infrastructure — Nanobot-Powered Cybersecurity",
    author="Ferrell Synthetic Intelligence",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "torch",
        "llama-cpp-python",
        "huggingface_hub",
        "transformers",
        "peft",
        "accelerate",
        "safetensors",
    ],
    entry_points={
        "console_scripts": [
            "jedi=jedi_cortex:main",
        ],
    },
)
