# LLM-DSL-Gen

## How to use

1. Clone the repository
```bash
git clone https://github.com/saturntsen/LLM-DSL-Gen.git && cd LLM-DSL-Gen
```
2. Setup
```bash
pip install -e .
```

3. configure environment variable

Edit the `config.example.toml` file, add your api keys, then save it as `config.toml`.

Then set the environment variable `LLM_DSL_CONFIG_PATH` to the path of the config file.

- Windows

```powershell
$Env:LLM_DSL_CONFIG_PATH = "/path/to/your/config.toml"
```
Or to set the environment variable permanently:

```powershell
[Environment]::SetEnvironmentVariable("LLM_DSL_CONFIG_PATH", "/path/to/your/config.toml", "User")
```

- Linux/MacOS

```bash
export LLM_DSL_CONFIG_PATH=/path/to/your/config.toml
```

Or to set the environment variable permanently:

```bash
echo 'export LLM_DSL_CONFIG_PATH=/path/to/your/config.toml' >> ~/.bashrc
source ~/.bashrc
```

3. Test

```bash
cd tests
python -m unittest discover
```

or run a specific test
```bash
cd tests
python -m unittest test test_llm_completion
```

4. Run

See notebooks in `notebooks/tests.ipynb` for more examples.

```python
from dsl_gen.core.flows import build_rag_flow
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')  

flow = build_rag_flow()
result = flow.invoke({"challenge_path": "/path/to/challenges/c001.json"})  
print(result["compiled"])
```

## Ollama backend setup

To execute the full test, you need to setup the Ollama backend.

1. Download and install the Ollama backend from `https://ollama.com/download`
2. Run the Ollama backend as a service
```bash
ollama run deepseek-r1:7b
ollama serve
```