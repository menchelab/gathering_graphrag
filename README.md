## Setup Google GenAI API Key

1.  **Obtain API Key**
    * Navigate to [Google AI Studio](https://aistudio.google.com/).
    * Log in with a Google account.
    * Select **Get API key** from the sidebar menu.
    * Click **Create API key**.
    * Select **Create API key in new project** (or select an existing project if preferred).
    * Copy the generated key string.

2.  **Configure Environment**
    * Create a file named `.env` in the root of the project directory.
    * Add the following line, replacing `<YOUR_API_KEY>` with the key copied in the previous step:

    ```bash
    GOOGLE_API_KEY=<YOUR_API_KEY>
    ```

    > **Note:** Ensure `.env` is listed in your `.gitignore` file to prevent committing credentials to version control.
