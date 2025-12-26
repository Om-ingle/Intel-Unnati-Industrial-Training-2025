import numpy as np 


from adapter.adapter import Adapter
from reader.reader import Reader 
from embedder.embedder import Embedder
from vector_database.vector_database import VectorDB

import nltk
nltk.download('punkt_tab')


# Reading or parsing a PDF 
pdf_reader = Reader("test.pdf")
texts = pdf_reader.extract_text()


# Testing Adapter 
# You can choose your chunking strategy by setting the 'splitter' parameter.
# Available options: "simple", "overlap", "token", "recursive"
adapter_instance = Adapter(chunk_size = 500, splitter="token")


# Tested the overlapping is happending and breaking down into chunks. 
text_docs, texts = adapter_instance.get_chunks(texts)




# Testing the embedder
embedder = Embedder()
embedded_docs_texts = embedder.embed_documents(text_docs)


# Testing the Qdrant Database 
vector_db = VectorDB(path = 'vector_database/data', collection_name = "test_rec")
vector_db.insert_docs_embeddings(embedded_docs_texts, texts)