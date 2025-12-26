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
vector_db = VectorDB(similarity_method="cosine", path = 'vector_database/data', collection_name = "test_reranker")
vector_db.insert_docs_embeddings(embedded_docs_texts, texts)