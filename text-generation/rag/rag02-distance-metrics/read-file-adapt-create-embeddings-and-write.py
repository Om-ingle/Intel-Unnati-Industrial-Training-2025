import numpy as np 


from adapter.adapter import Adapter
from reader.reader import Reader 
from embedder.embedder import Embedder
from vector_database.vector_database import VectorDB 


# Reading or parsing a PDF 
pdf_reader = Reader("test.pdf")
texts = pdf_reader.extract_text()


# Testing Adapter 
adapter_instance = Adapter(chunk_size = 500)


# Tested the overlapping is happending and breaking down into chunks. 
text_docs, texts = adapter_instance.get_chunks(texts)


# Testing the embedder
embedder = Embedder()
embedded_docs_texts = embedder.embed_documents(text_docs)


# Testing the Qdrant Database 
# You can choose the distance metric for similarity search by setting the 'similarity_method' parameter.
# Available options: "cosine", "dot", "euclidean", "manhattan"
vector_db = VectorDB(path='vector_database/data', collection_name="test_dist_metrics", similarity_method="cosine")
vector_db.insert_docs_embeddings(embedded_docs_texts, texts)