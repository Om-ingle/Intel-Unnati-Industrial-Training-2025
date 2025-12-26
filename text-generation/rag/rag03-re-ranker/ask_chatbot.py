from vector_database.vector_database import VectorDB 
from embedder.embedder import Embedder
from llm.serve_llm import LLM 
from re_ranker.re_ranker import ReRankerComponent

llm = LLM()

embedder = Embedder()

vector_db = VectorDB(similarity_method="dot", path = 'vector_database/data', collection_name = "test_reranker")


while True: 

    # QUERY = "What are the power supplies requirement of XR11 and XR12?"
    QUERY = input("Ask question to the bot! -  ")
    query_embedding = embedder.encode_query(QUERY)

    top_k = vector_db.query_embeddings(query_embedding, limit=10)
    top_chunks_list = [point.payload['text'] for point in top_k]
    top_chunks_string = '\n'.join(top_chunks_list)

    file_name = "outputs.txt"

    model_name = "BAAI/bge-large-en-v1.5"

    top_n = 3
    re_ranker  = ReRankerComponent(model_name = model_name)
    re_ranked_list = re_ranker._rerank(model_name=model_name, query=QUERY, chunks = top_chunks_list, top_n=top_n)



    with open(file_name, "w") as file:
        
        file.write("THE CHUNKS BEFORE RE-RANKING " + "\n\n\n")
        for chunk in top_chunks_list:
            
            file.write(chunk + "\n\n")
            
        file.write("THIS IS AFTER RE-RANKING\n\n\n")
        for re_ranked_chnuk in re_ranked_list:
            file.write(re_ranked_chnuk + "\n\n")
    
    print("LLM Response : ")
    answer_to_query = llm.generate_answer(QUERY, re_ranked_list)
    print(f"\n\nANSWER TO THE QUERY : {answer_to_query}")