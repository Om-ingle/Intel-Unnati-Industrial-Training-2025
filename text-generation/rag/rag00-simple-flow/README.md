# Simple RAG Pipeline

This document outlines a basic Retrieval-Augmented Generation (RAG) pipeline. The pipeline consists of two main processes:

1.  **Ingestion**: Reading a document, chunking it, creating embeddings, and storing them in a vector database.
2.  **Retrieval and Generation**: Taking a user query, retrieving relevant text chunks from the vector database, and using a Large Language Model (LLM) to generate an answer.

## Setup

This project uses `uv` for package management. If you don't have it installed, you can install it with:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Environment Setup and Dependencies

1.  Create a virtual environment:
    ```bash
    uv venv
    ```

2.  Activate the virtual environment:
    ```bash
    source .venv/bin/activate
    ```

3.  Install the required dependencies from `requirements.txt`:
    ```bash
    uv pip install -r requirements.txt --torch-backend=cpu
    ```

## Pipeline Workflow

The pipeline is split into two main Python scripts:

1.  `read-file-adapt-create-embeddings-and-write.py`: For data ingestion.
2.  `ask_chatbot.py`: For querying the RAG pipeline.

### 1. Ingestion: Creating and Storing Embeddings

The `read-file-adapt-create-embeddings-and-write.py` script performs the following steps:

1.  **Read Document**: It uses the `Reader` class to read a PDF file (`test.pdf`) and extract the text content.
2.  **Chunk Text**: The `Adapter` class takes the extracted text and splits it into smaller, overlapping chunks of a specified size.
3.  **Generate Embeddings**: The `Embedder` class converts the text chunks into numerical vector embeddings.
4.  **Store Embeddings**: The `VectorDB` class (using Qdrant) is used to store these embeddings in a vector database for efficient retrieval.

To run the ingestion process:

```bash
python read-file-adapt-create-embeddings-and-write.py
```

### 2. Retrieval and Generation: Asking a Question

The `ask_chatbot.py` script allows you to ask questions and get answers from the pipeline:

1.  **Encode Query**: When you input a question, the `Embedder` converts your query into an embedding.
2.  **Retrieve Chunks**: The `VectorDB` searches the vector database for the most similar text chunk embeddings to your query embedding.
3.  **Generate Answer**: The retrieved text chunks and your original query are passed to the `LLM` (Large Language Model), which generates a coherent answer based on the provided context.

To start the interactive chatbot:

```bash
python ask_chatbot.py
```

You will be prompted to enter your questions in the terminal.
