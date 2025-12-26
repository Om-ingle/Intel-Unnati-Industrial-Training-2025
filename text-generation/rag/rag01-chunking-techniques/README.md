# RAG Pipeline - Chapter 1: Advanced Chunking Techniques

This chapter builds upon the simple RAG pipeline from Chapter 0 by introducing more sophisticated text chunking techniques. Effective chunking is crucial for improving the relevance of retrieved context and, consequently, the quality of the generated answer.

## Progression from Chapter 0

In the previous chapter, we used a basic, fixed-size chunking method. In this chapter, the `adapter.py` script is enhanced to include multiple advanced chunking strategies:

*   **`SimpleChunker`**: The baseline fixed-size chunker.
*   **`OverlapTextSplitter`**: Creates overlapping chunks to maintain context between them.
*   **`TokenSplitter`**: Chunks text based on token count, often aligning better with model input limits. It uses `nltk` for sentence tokenization.
*   **`RecursiveCharacterTextSplitter`**: A more advanced method that recursively splits text by a list of separators (e.g., `

`, `
`, `.`, ` `), attempting to keep related text together.

The `read-file-adapt-create-embeddings-and-write.py` script now defaults to using the `RecursiveCharacterTextSplitter`.

## Setup

This project uses `uv` for package management.

### Environment Setup and Dependencies

1.  Create a virtual environment:
    ```bash
    uv venv
    ```

2.  Activate the virtual environment:
    ```bash
    source .venv/bin/activate
    ```

3.  Install the required dependencies. Note that `nltk` has been added for the `TokenSplitter`.
    ```bash
    uv pip install -r requirements.txt --torch-backend=cpu
    ```
4. Download `nltk` tokenizer data:
   The `TokenSplitter` requires the `punkt` sentence tokenizer from `nltk`. Run the following command to download it:
   ```bash
   python -m nltk.downloader punkt
   ```

## Pipeline Workflow

The overall workflow remains the same as in Chapter 0, but the chunking step is now more advanced.

### 1. Ingestion: Creating and Storing Embeddings

The `read-file-adapt-create-embeddings-and-write.py` script handles the ingestion process. A key improvement in this chapter is the ability to choose your chunking strategy.

#### Configuring the Chunker

You can select the desired chunking method by setting the `splitter` parameter when creating an `Adapter` instance in the `read-file-adapt-create-embeddings-and-write.py` script.

Available `splitter` options are:
*   `"simple"`: `SimpleChunker`
*   `"overlap"`: `OverlapTextSplitter`
*   `"token"`: `TokenSplitter`
*   `"recursive"`: `RecursiveCharacterTextSplitter` (Default)

Here is how you can configure it in the script:
```python
# In read-file-adapt-create-embeddings-and-write.py

# You can choose your chunking strategy by setting the 'splitter' parameter.
adapter_instance = Adapter(chunk_size=500, splitter="recursive") 
```

To run the ingestion process with your chosen chunker:

```bash
python read-file-adapt-create-embeddings-and-write.py
```

### 2. Retrieval and Generation: Asking a Question

The `ask_chatbot.py` script remains unchanged and allows you to interact with the RAG pipeline. It will now leverage the embeddings created from the recursively split chunks.

To start the interactive chatbot:

```bash
python ask_chatbot.py
```
