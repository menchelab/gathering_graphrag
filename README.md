# GraphRAGs gathering

Authors: Simon Schindler, Ariadna Villanueva

## Introduction

**RAGs**

Large language models (LLMs) achieve strong performance across many tasks by encoding knowledge in their parameters, but they often fail when required information lies outside their training data or is outdated. Retrieval-augmented generation (RAG) was developed to address this limitation by combining LLMs with external knowledge sources. In a RAG framework, relevant documents are retrieved from a database and provided to the model at inference time, grounding the generated output in explicit evidence. This approach improves task performance, enables access to up-to-date information, and reduces hallucinations.

Limitations: RAG systems may still misinterpret retrieved content, for example by extracting statements with missing context. When sources provide conflicting or temporally inconsistent information, the model may struggle to assess reliability, potentially producing responses that blend outdated and current facts in a misleading way.

Technically, RAG systems consist of two main components: a retriever and a generator. Documents are first preprocessed by splitting them into chunks and converting each chunk into a vector embedding using an embedding model. These embeddings are stored in a vector database. At inference time, the user query is embedded in the same vector space and used to retrieve the most relevant document chunks via similarity search. The retrieved content is then appended to the prompt and passed to the large language model, which generates a response conditioned on both the query and the retrieved context.

![RAG diagram](https://en.wikipedia.org/wiki/Retrieval-augmented_generation#/media/File:RAG_diagram.svg "Diagram")

*Image source: Wikimedia Commons, CC BY-SA 4.0*

**Related sources:**

1. https://research.ibm.com/blog/retrieval-augmented-generation-RAG
2. Lewis, P., et al. (2020). Retrieval-augmented generation for knowledge-intensive NLP tasks. In Proceedings of the 34th International Conference on Neural Information Processing Systems. Curran Associates Inc.




## Organization

We will first go through the tutorial, that we have divided into two notebooks:
- Knowledge graphs: 01_knowledge_graph_construction.ipynb
- RAGs: 02_graph_retrieval_augmented_generation.ipynb

**Challenges:**

You can select any of these challenges ordered by increasing level of difficulty.

1. Create a knowledge graph for another disease of your choice
2. Create your own knowledge database for papers relevant to your project
3. Navigate the Human reference atlas Knowledge Graph: https://docs.humanatlas.io/dev/kg#accessing-the-hra-kg
4. Create a network on genes based on common pathways
5. Make up your own challenge

**Tasks:**

0. Fork this repo if you want to show your solution (optional)
1. Set up the environment
2. Set up the Gemini API keys. If you have a OpenAI API you can also use it.
3. Go through the notebooks
4. Do one of the challenge
5. Share your solution ()



**Outcomes:**

- Learn about graphRAGs


## Environment Setup

Ensure you are in the root directory of the repository (`gathering_graphrag`) before running the following commands.

### Option 1: Using `uv` (Recommended)

This project utilizes `uv` for dependency management, ensuring reproducible environments via `uv.lock`.

```bash
# Install uv if not already installed
curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh

# Sync dependencies and create the virtual environment
uv sync

# Activate the environment
source .venv/bin/activate

```

### Option 2: Using `conda`

If you prefer Conda, create an environment and install dependencies using `requirements.txt`.

```bash
# Create and activate a new environment
conda create -n gathering_graphrag python=3.10
conda activate gathering_graphrag

# Install dependencies
pip install -r requirements.txt

```

### Option 3: Using `venv`

Standard Python virtual environment setup using `requirements.txt`.

```bash
# Create the virtual environment
python -m venv .venv

# Activate the environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

```

## Neo4j Aura Setup

1. **Create Account**
    * Navigate to the [Neo4j Aura Console](https://console.neo4j.io/).
    * Click **Start for Free**.
    * Select **Sign in with Google** and authenticate with your existing Google credentials.

2. **Create Database Instance**
    * Once logged in, click **New Instance**.
    * Select the **Free** tier.
    * Choose a region close to your location.
    * Click **Create Instance**.

3. **Retrieve Credentials**
    * A modal will appear displaying your generated password. **Copy and save this password immediately**, as it is shown only once.
    * Wait for the instance status to change to **Running**.
    * Copy the **Connection URI** displayed on the dashboard (e.g., `neo4j+s://<db_id>.databases.neo4j.io`).

4. **Configure Environment**
    * Open the `.env` file in the root directory.
    * Append the following variables, replacing the placeholders with your specific instance details:

    ```bash
    NEO4J_URI=<YOUR_CONNECTION_URI>
    NEO4J_USERNAME=neo4j
    NEO4J_PASSWORD=<YOUR_GENERATED_PASSWORD>
    ```

## Setup Google GenAI API Key

1. **Obtain API Key**
    * Navigate to [Google AI Studio](https://aistudio.google.com/).
    * Log in with a Google account.
    * Select **Get API key** from the sidebar menu.
    * Click **Create API key**.
    * Select **Create API key in new project** (or select an existing project if preferred).
    * Copy the generated key string.

2. **Configure Environment**
    * Create a file named `.env` in the root of the project directory.
    * Add the following line, replacing `<YOUR_API_KEY>` with the key copied in the previous step:

    ```bash
    GOOGLE_API_KEY=<YOUR_API_KEY>
    ```

    > **Note:** Ensure `.env` is listed in your `.gitignore` file to prevent committing credentials to version control.

3. Test the setup
    * Test your setup by running:

    ```bash
    python scripts/test_api_keys.py
    ```

## Sources
- Tutorial from Neo4j: https://neo4j.com/blog/news/graphrag-python-package/
- Hugging face tutorial: https://huggingface.co/learn/cookbook/rag_with_knowledge_graphs_neo4j


## Additional interesting pages:

- If you want to run your AuraDB locally with docker: https://blog.greenflux.us/building-a-knowledge-graph-locally-with-neo4j-and-ollama/
