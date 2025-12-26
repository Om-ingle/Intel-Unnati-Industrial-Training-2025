from vector_database.vector_database import VectorDB 
from embedder.embedder import Embedder
from llm.serve_llm import LLM 

llm = LLM()

embedder = Embedder()

vector_db = VectorDB(path = 'vector_database/data', collection_name = "test3")


while True: 

    # QUERY = "What are the power supplies requirement of XR11 and XR12?"
    QUERY = input("Ask question to the bot! -  ")
    query_embedding = embedder.encode_query(QUERY)

    top_k = vector_db.query_embeddings(query_embedding)
    top_chunks_list = [point.payload['text'] for point in top_k]
    top_chunks_string = '\n'.join(top_chunks_list)
    print(f"Top chunks are: {top_chunks_string}")

    answer_to_query = llm.generate_answer(QUERY, top_chunks_list)
    print(f"\n\nANSWER TO THE QUERY : {answer_to_query}")
