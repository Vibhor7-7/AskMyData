"""
Embeddings Module - Generate vector embeddings using Ollama

What does this do?
- Takes text chunks
- Sends them to Ollama embedding model
- Gets back numerical vectors (lists of numbers)
- These vectors capture semantic meaning
"""

import ollama 
from typing import List, Dict
import numpy as np 


class EmbeddingGenerator: 
    """
    - Class to Handle Embeddings Generation 

    Why a Class?
     - Keeps connection to Ollama
    - Reuses model without reloading
    - Handles batching and errors
    """

    def __init__(self, model_name: str = "nomic-embed-text"): 
        self.model_name = model_name 
        self.embedding_dim = 768 # Nomic-emded-text outputs 768 dimensional vectors 

        try: 
            test_embedding = self.embed("test")
            print(f" Embedding model {model_name} is working")
            print(f" Embedding dimension: {len(test_embedding)}")

        except Exception as e: 
            print(f"Error loading the model: {e}")
            print("Make Sure Ollama is Running, run: ollama serve")
            raise 

    def embed(self, text: str) -> list[float]: 
        """
        Generate embedding for a single text
            
        Args:
            text: Input text string
            
        Returns:
            List of floats (the embedding vector)
        """

        try: 
            response = ollama.embeddings(
                model = self.model_name,
                prompt=text
            )
            return response['embedding']
        except Exception as e: 
            print(f"Error Occured while generating embedding: {e}")
            return [0.0] * self.embedding_dim # Return zero vector on error 
    
    def embed_batch(self, texts: List[str]) -> List[List[float]]: 
        """
        Generate embeddings for mutiple texts 

        Args: 
            texts: List of text strings 
        Returns: 
            List of embedding vectors
        """
        embeddings = []
        total = len(texts)

        for i, text in enumerate(texts, 1): 
            if i%10 ==0: # Cool progress indicator 
                print(f"Embedding {i}/{total}...")

            embedding = self.embed(text)
            embeddings.append(embedding)
        return embeddings 

    def embed_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """
        Add embeddings to chunk dictionaries
        
        Args:
            chunks: List of chunk dicts from chunking.py
        
        Returns:
            Same chunks with 'embedding' field added
        """
        print(f"Generating embeddings for {len(chunks)} chunks...")
        
        # Extract just the text
        texts = [chunk['text'] for chunk in chunks]
        
        # Generate embeddings
        embeddings = self.embed_batch(texts)
        
        # Add embeddings back to chunks
        for chunk, embedding in zip(chunks, embeddings):
            chunk['embedding'] = embedding
        
        print(" Embeddings generated successfully!")
        return chunks

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate similarity between two embeddings
    
    Returns value between -1 (opposite) and 1 (identical)
    0.8+ = very similar
    0.5-0.8 = somewhat similar
    <0.5 = not very similar

    Use Numpy to help with calculations 
    """
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    return dot_product / (norm1 * norm2)

def main(): 
    """Test the embedding generator"""
    
    # Initialize
    embedder = EmbeddingGenerator()
    
    # Test with sample texts
    sample_chunks = [
        {
            'text': 'name: Alice, age: 25, city: NYC',
            'metadata': {'chunk_id': 'test_1'}
        },
        {
            'text': 'name: Bob, age: 30, city: LA',
            'metadata': {'chunk_id': 'test_2'}
        }
    ]
    
    # Generate embeddings
    chunks_with_embeddings = embedder.embed_chunks(sample_chunks)
    
    # Display results
    print("\n=== Embedding Results ===")
    for chunk in chunks_with_embeddings:
        print(f"\nChunk: {chunk['text']}")
        print(f"Embedding (first 5 values): {chunk['embedding'][:5]}")
        print(f"Embedding dimension: {len(chunk['embedding'])}")
    
    # Test similarity
    print("\n=== Similarity Test ===")
    similarity = cosine_similarity(
        chunks_with_embeddings[0]['embedding'],
        chunks_with_embeddings[1]['embedding']
    )
    print(f"Similarity between chunks: {similarity:.4f}")


if __name__ == "__main__":
    main()