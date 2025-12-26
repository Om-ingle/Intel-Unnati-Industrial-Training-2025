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

print(type(embedded_docs_texts))


# Testing the Qdrant Database 
vector_db = VectorDB(path = 'vector_database/data', collection_name = "test3")
vector_db.insert_docs_embeddings(embedded_docs_texts, texts)