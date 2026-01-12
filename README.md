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

3. Test the Key
    * Test your setup by running:

    ```bash
    python scripts/test_api_key.py
    ```
