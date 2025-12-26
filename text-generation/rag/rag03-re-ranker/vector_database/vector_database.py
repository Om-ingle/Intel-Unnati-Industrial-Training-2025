from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    VectorParams,
)
import os 
from qdrant_client.models import PointStruct
from typing import List 


class VectorDB: 
    def __init__(self,similarity_method: str, path: str = 'data', collection_name: str = "RAG", embedding_size: int = 1024, verbose: bool = True): 
        self.collection_name = collection_name
        self.verboseprint = print if verbose else lambda *a: None
        self.client = QdrantClient(path = path)
      
        similarity_method_lower = similarity_method.lower()
        distance_mapping = {
            "cosine": Distance.COSINE,
            "dot": Distance.DOT,
            "manhattan": Distance.MANHATTAN,
        }
        self.distance = distance_mapping.get(similarity_method_lower, Distance.EUCLID)

        if os.path.exists(os.path.join(path, 'collection', collection_name)):
            self.verboseprint(f"Database Loaded")
        else:
            self.client.recreate_collection(
                collection_name = self.collection_name, 
                vectors_config = VectorParams(size = embedding_size, distance = self.distance)
            )
            self.verboseprint(f"Vector Database {self.collection_name} initialized.")
     
    
    def insert_docs_embeddings(self, embeddings: List, metadata = None):
        self.client.upsert(
            collection_name = self.collection_name, 
            points = [
                PointStruct(
                    id = idx,
                    vector = embeds.tolist(), 
                    payload = {'text': text}
                )
                for idx, (embeds, text) in enumerate(zip(embeddings, metadata))
            ]
        )
        self.verboseprint(f'Embedding stored.')

    
    def query_embeddings(self, query_embedding: List, limit: int): 
        retrieved_embeddings = self.client.search( 
            collection_name = self.collection_name, 
            query_vector = query_embedding, 
            with_vectors=True,
            limit = limit
        )
        return retrieved_embeddings
    
