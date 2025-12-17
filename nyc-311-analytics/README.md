# NYC 311 Data Analytics Agent

A conversational AI agent that analyzes NYC 311 complaint data using LangGraph, DuckDB, and DeepSeek API.

## Setup

1.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Environment Variables**
    Ensure `.env` contains your DeepSeek API key:
    ```
    DEEPSEEK_API_KEY=your_key_here
    DEEPSEEK_API_BASE=https://api.deepseek.com/v1
    ```

3.  **Data**
    Download the NYC 311 Service Requests dataset (CSV) and place it in `data/nyc_311_data.csv`.

## Running the Application

```bash
streamlit run app.py
```

## Features

-   **Natural Language Queries**: Ask questions in plain English.
-   **SQL Generation**: Automatically converts questions to DuckDB SQL queries.
-   **Data Visualization**: Generates charts (Bar, Line) when appropriate.
-   **Interactive UI**: Built with Streamlit for easy interaction.

## Project Structure

-   `src/agent.py`: LangGraph workflow definition.
-   `src/database.py`: DuckDB connection and query execution.
-   `src/llm_client.py`: DeepSeek API integration.
-   `app.py`: Streamlit frontend.
