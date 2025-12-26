# RAG Pipeline - Chapter 2: Distance Metrics

This chapter enhances our RAG pipeline by introducing the ability to configure different distance metrics for similarity search in the vector database. The choice of metric determines how "similarity" between the query and the document chunks is calculated, which can significantly impact retrieval quality.

## Progression from Chapter 1

While Chapter 1 focused on *how* to chunk text, this chapter focuses on *how to measure similarity* for the resulting embeddings. We have updated the `VectorDB` class to allow the selection of a distance metric when the database is initialized.

The `vector_database/vector_database.py` script now supports the following metrics from Qdrant:
*   **Cosine Similarity**: Measures the cosine of the angle between two vectors. It is effective at finding documents that are thematically similar, regardless of their magnitude. This is often the default for text-based similarity.
*   **Dot Product**: Similar to Cosine but sensitive to vector magnitude. It can be useful when the magnitude of the embedding vector carries important information.
*   **Euclidean Distance (L2)**: Measures the straight-line distance between two points in space. It is a good all-around metric for many use cases.
*   **Manhattan Distance (L1)**: Measures distance by summing the absolute differences of the vector components. It's less sensitive to outliers than Euclidean distance.

## Setup

This project uses `uv` for package management.

### Environment Setup and Dependencies

1.  Create and activate a virtual environment:
    ```bash
    uv venv
    source .venv/bin/activate
    ```

2.  Install the required dependencies:
    ```bash
    uv pip install -r requirements.txt --torch-backend=cpu
    ```
3.  Download `nltk` tokenizer data (required for `TokenSplitter` from the previous chapter):
    ```bash
    python -m nltk.downloader punkt
    ```

## Pipeline Workflow

The workflow remains the same, but we now have control over a crucial hyperparameter in our vector database.

### 1. Ingestion: Creating the Vector Collection

The `read-file-adapt-create-embeddings-and-write.py` script now configures the distance metric when creating the `VectorDB` instance.

#### Configuring the Distance Metric

You can select the metric by setting the `similarity_method` parameter. This setting is only applied when the collection is **created for the first time**.

Available `similarity_method` options are:
*   `"cosine"` (Default)
*   `"dot"`
*   `"euclidean"`
*   `"manhattan"`

Example in `read-file-adapt-create-embeddings-and-write.py`:
```python
# You can choose the distance metric for similarity search.
vector_db = VectorDB(
    path='vector_database/data', 
    collection_name="test_dist_metrics", 
    similarity_method="cosine"
)
```

To run the ingestion process:
```bash
python read-file-adapt-create-embeddings-and-write.py
```

### 2. Retrieval and Generation: Asking a Question

The `ask_chatbot.py` script is unchanged. It will automatically use the distance metric that the collection was created with to retrieve the most relevant document chunks.

To start the interactive chatbot:
```bash
python ask_chatbot.py
```

