"""
Vitalis Cortex loader shim.

The upstream ``src/__init__.py`` pulls in a large framework we don't need
(and some root-level modules that aren't shipped with the JEDI bundle).
The only piece JEDI requires is ``src/brain/inference.py`` (InferenceEngine),
which depends only on numpy + llama_cpp. Load it directly from file so we
skip the heavy/optional package __init__ chain.
"""
import importlib.util
import os

_HERE = os.path.dirname(os.path.abspath(__file__))


def _load_inference_engine():
    path = os.path.join(
        _HERE, "Vitalis_LFM2.5_Cortex.GGUF", "src", "brain", "inference.py"
    )
    spec = importlib.util.spec_from_file_location("vitalis_brain_inference", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.InferenceEngine


InferenceEngine = _load_inference_engine()
