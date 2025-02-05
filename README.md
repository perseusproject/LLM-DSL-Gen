# LLM-DSL-Gen

## Change log

### v0.1.2 - 2025-02-05
- Defined APIs for other retrieval methods.
- Sanity check on each node's entry.
- Defined error handling in the flow (Not implemented yet)
- Better logging

### v0.1.1 - 2025-02-05
- Added safe print for `SimpleNamespace` to protect your API keys
- Added setup support for macOS and Linux

### v0.1.0 - 2025-02-03
- Added support for OpenAI, Ollama, and DeepSeek models
- Included configuration setup and environment variable instructions
- Provided example usage and testing instructions

## Future work

- Basic functionalities
    - TODO: Implement test modules for evaluation (Test-Driven Development Let's Go!)
    - TODO: Refine error handling in the RAG flow
- Better RAG:
    - TODO: Improve Faiss vector database construction for better performance
    - TODO: Add refs to the RAG flow for better completion results
- Visualization:
    - TODO: Implement a visualization module for the RAG result
- Evaluation:
    - TODO: Implement a AIO pipeline for evaluation

## Installation

0. (Optional) Create a virtual environment

```bash
conda create -n dsl-gen python=3.10.11
conda activate dsl-gen
```

1. Clone the repository
```bash
git clone https://github.com/saturntsen/LLM-DSL-Gen.git && cd LLM-DSL-Gen
```
2. Setup
```bash
pip install -e .
```

3. Edit Config

Edit the `api.example.toml` file, add your api keys,  and save it as `api.toml`.

```toml
# OpenAI Configuration
[MODEL_CFG.OpenAI]
model = "gpt-3.5-turbo"
api_key = "sk-xxxx"
base_url = "https://api.openai.com/v1"

# Ollama Configuration
[MODEL_CFG.Ollama]
model = "deepseek-r1:7b"
api_key = "placeholder"
base_url = "http://localhost:11434/v1"

# DeepSeek Configuration
[MODEL_CFG.DeepSeek]
model = "deepseek-ai/DeepSeek-R1"
api_key = "sk-xxxx"
base_url = "https://api.siliconflow.com/v1"
```

Edit the `config.example.toml` file, rename the paths to the correct paths, and save it as `config.toml`.

Example:

```toml
[PATH_CFG]
TUTO_PATH = "D:/Projects/PSC/LLM-DSL-Gen/docs"
REF_PATH = "D:/Projects/PSC/LLM-DSL-Gen/refs"
CHALLENGES_PATH = "D:/Projects/PSC/LLM-DSL-Gen/benchmarks/challenges"
VECTOR_DB_DIR = "D:/Projects/PSC/LLM-DSL-Gen/vector_db"
```

4. Set Environment Variable

Then set the environment variable `LLM_DSL_CONFIG_PATH` and `api.example.toml` to the path of the config file.

- Windows

```powershell
$Env:LLM_DSL_CONFIG_PATH = "/path/to/your/config.toml"
$Env:LLM_DSL_API_PATH = "/path/to/your/api.toml"
```
Or to set the environment variable permanently:

```powershell
[Environment]::SetEnvironmentVariable("LLM_DSL_CONFIG_PATH", "/path/to/your/config.toml", "User")
[Environment]::SetEnvironmentVariable("LLM_DSL_API_PATH", "/path/to/your/api.toml", "User")
```

- Linux/MacOS

```bash
export LLM_DSL_CONFIG_PATH="/path/to/your/config.toml"
export LLM_DSL_API_PATH="/path/to/your/api.toml"
```

Or to set the environment variable permanently:
```bash
LLM_DSL_CONFIG_PATH="/path/to/your/config.toml"
LLM_DSL_API_PATH="/path/to/your/api.toml"

if [ -n "$BASH_VERSION" ]; then
    CONFIG_FILE=~/.bashrc
elif [ -n "$ZSH_VERSION" ]; then
    CONFIG_FILE=~/.zshrc
fi

if [ -n "$CONFIG_FILE" ]; then
    echo "export LLM_DSL_CONFIG_PATH=\"$LLM_DSL_CONFIG_PATH\"" >> "$CONFIG_FILE"
    echo "export LLM_DSL_API_PATH=\"$LLM_DSL_API_PATH\"" >> "$CONFIG_FILE"
    source "$CONFIG_FILE"
fi
```
<span style="color:red">Note: You need to restart your terminal as well as your Editor/IDE to make the environment variable take effect!</span>

## Usage

See notebooks in `notebooks/workflow.ipynb` for more examples.

```python
from dsl_gen.core.flows import build_rag_flow
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')  

flow = build_rag_flow()
result = flow.invoke({"challenge_path": "/path/to/challenges/c001.json"})  
print(result["compiled"])
```

## Testing

```bash
cd tests
python -m unittest discover
```

or run a specific test
```bash
cd tests
python -m unittest test test_llm_completion
```

## How to collaborate: Pull Request

1. Fork the repository
```bash
git clone https://github.com/saturntsen/LLM-DSL-Gen.git
cd LLM-DSL-Gen
```

2. Create a new branch
```bash
git checkout -b feature-xxx
```

3. Make your changes
```bash
git add .
git commit -m "Add new feature/fix bug"
git push origin feature-xxx
```

4. Create a Pull Request

Go to the [repository](https://github.com/saturntsen/LLM-DSL-Gen) and create a new Pull Request.

5. Wait for the review

## (Optional) Ollama backend setup

To execute the full test or if you want to run an LLM locally, you need to setup the Ollama backend.

1. Download and install the Ollama backend from `https://ollama.com/download`
2. Run the Ollama backend as a service

```bash
ollama run deepseek-r1:7b
ollama serve
```

