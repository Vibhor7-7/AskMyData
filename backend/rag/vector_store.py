"""
Vector Store Module - Store and retrieve embeddings using Chroma 

What is Chroma?
- Database specfically designed for embeddings 
- Finds similar items using vector math 
"""

import chromadb 
from chromadb.config import Settings 
from typing import List, Dict 
import os 

class VectorStore: 
    """
    Manages storage and retrieval of embeddings 
    """

    def __init__(self, persist_directory: str = "./chroma_db"): 
        """
        Initialize chroma database 
        
        Args:
            persist_directory: Where to save the database on disk 
        """

        os.makedirs(persist_directory, exist_ok=True) # Create Directory if it doesn't exist 
        self.client = chromadb.PersistentClient(path = persist_directory)
        print(f'Chroma initialized at: {persist_directory}')

    def create_collection(self, collection_name: str, reset: bool=False ): 
        """
        Create or get a collection (like a table in SQL)
        
        Args:
            collection_name: Name for this collection (e.g., "user123_data")
        """
        if reset: 
            try: 
                self.client.delete_collection(collection_name)
                print(f" Deleted existing collection: {collection_name}")
            except: 
                pass 
        
        self.collection = self.client.get_or_create_collection(

            name = collection_name,
            metadata = {"descripion": "User uploaded data chunks"}
        )
    
        print(f" Collection {collection_name} is ready")
        return self.collection 
    
    def add_chunks(self, chunks: List[Dict]):
        """
        Add chunks with embeddings to the database
        
        Args:
            chunks: List of dicts with 'text', 'embedding', and 'metadata'
        """
        if not hasattr(self, 'collection'):
            raise ValueError("No collection selected. Call create_collection() first. ")
        
        # Extract date from chunks 
        ids=[chunk['metadata']['chunk_id'] for chunk in chunks]
        embeddings = [chunk['embedding'] for chunk in chunks]
        documents = [chunk['text'] for chunk in chunks]
        metadatas = [chunk['metadata'] for chunk in chunks]

        #Remove 'embeddings' from metadata since its stored separately 
        for metadata in metadatas: 
            if 'embedding' in metadata: 
                del metadata['embedding']
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        print(f' Added {len(chunks)} chunks to collection {self.collection.name}')

    def search(self, query_embedding: List[float], top_k: int =5, where_filter: Dict = None)->Dict: 
        """
        Search for similar chunks using query embedding 

        Args: 
            query_embedding: Embedding of user's question 
            top_k: Number of results to return (sort of like pd.head())
            where_filter: Optional metadata filter (e.g., {"filename": "data.csv"})
        
        Returns: 
            Dict with 'documents', 'metadatas', and 'distances' 
        """
        if not hasattr(self, 'collection'):
            raise ValueError("No collection seleted.")
        
        query_params = {
            "query_embeddings": [query_embedding],
            "n_results": top_k
        }
        
        if where_filter:
            query_params["where"] = where_filter
        
        results = self.collection.query(**query_params)

        return {
            'documents': results['documents'][0],  # Actual text chunks
            'metadatas': results['metadatas'][0],  # Metadata for each chunk
            'distances': results['distances'][0]   # How similar (lower = more similar)
        }

    def get_collection_stats(self)->Dict:
        """
        Get Stats about the current collection 
        """
        if not hasattr(self, 'collection'):
            raise ValueError("No collection seleted.")
        
        count = self.collection.count()
        return{
            "name": self.collection.name,
            "count": count, 
            "metadata": self.collection.metadata
        }   
    
def main():
    from embeddings import EmbeddingGenerator
    # Initialize
    embedder = EmbeddingGenerator()
    vector_store = VectorStore(persist_directory="./test_chroma_db")
    vector_store.create_collection("test_collection", reset=True)

    sample_chunks = [
    {'text': 'name: Alice, age: 25, city: NYC', 'metadata': {'chunk_id': 'c1'}},
    {'text': 'name: Bob, age: 30, city: LA', 'metadata': {'chunk_id': 'c2'}},
    {'text': 'name: Charlie, age: 35, city: Chicago', 'metadata': {'chunk_id': 'c3'}}
    ]

    #Add embeddings 
    chunks_with_embeddings = embedder.embed_chunks(sample_chunks)
    #Store in Chroma 
    vector_store.add_chunks(chunks_with_embeddings)
    #Test search 
    print("\n ===Testing Search===")
    query = "Who lives in new york?"
    query_embedding = embedder.embed(query)

    results = vector_store.search(query_embedding, top_k = 2)

    print(f"\nQuery: {query}")
    print(f"\nTop {len(results['documents'])} results:")
    for i, (doc, meta, dist) in enumerate(zip(
        results['documents'],
        results['metadatas'],
        results['distances']
    ), 1):
        print(f"\n{i}. {doc}")
        print(f"   Distance: {dist:.4f}")
        print(f"   Metadata: {meta}")

    # Show stats
    print("\n=== Collection Stats ===")
    print(vector_store.get_collection_stats())

if __name__ =="__main__":
    main()
        
