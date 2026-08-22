# IKEAssist

IKEAssist is a retrieval-augmented generation (RAG) assistant for IKEA products.
It searches the product dataset for relevant product
descriptions, then gives those results to the Llama3.2 LLM model to generate an
answer. 

LangChain connects the product search with the question-answering process,
while Ollama provides the models used to find relevant products and generate
answers. Product embeddings are stored in a persistent Chroma vector database,
so the dataset is indexed automatically on the first run and reused afterward.

## Data Citation

The data is a static snapshot of IKEA US Products in July 2025 in CommerceTXT format.

Data source: 

@dataset{ikea_us_commercetxt_2025,
  title = {IKEA US CommerceTXT Dataset},
  author = {Tsanko Zanov},
  year = {2026},
  url = {https://huggingface.co/datasets/tsazan/ikea-us-commercetxt}
}

The data is a CommerceTXT adaptation of the original dataset below:

@misc{ikea_us_products_2025,
  title = {IKEA US Product Dataset (July 2025)},
  author = {Jeffrey Zhou},
  year = {2025},
  url = {https://huggingface.co/datasets/jeffreyszhou/ikea-us-products-2025}
}


## Project Files

- `main.py` - interactive question-and-answer loop
- `vector.py` - product parsing, embeddings, Chroma storage, and retrieval
- `hf_data/products` - local product data used as the knowledge base
- `requirements.txt` - Python dependencies

## How It Works

1. Product files in `hf_data/products` are parsed into product, offer, and
	specification text.
2. `mxbai-embed-large` creates embeddings through Ollama.
3. Chroma retrieves the five closest product documents for each question.
4. `llama3.2` answers using the retrieved product context.

## Requirements

- Python 3.10 or newer
- [Ollama](https://ollama.com/) installed and running
- The required Ollama models:

```text
llama3.2
mxbai-embed-large
```

## Installation

Clone the repository and open a terminal in its root directory:

```bash
python -m venv .venv
```

Activate the virtual environment.

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install the Python dependencies:

```bash
python -m pip install -r requirements.txt
```

Install and start Ollama, then download the models:

```bash
ollama pull llama3.2
ollama pull mxbai-embed-large
```

## Run the Assistant

From the project root, with the virtual environment activated:

```bash
python main.py
```

Enter a question when prompted, for example:

```text
Ask your question (q to quit): Which desks are suitable for a small room?
```

Type `q` to quit.

On the first run, IKEAssist creates and populates `chroma_db_ikea`. Later runs
reuse that database and start more quickly.

