"""
Query Processor Module 

Main Modue that ties everything toegether: 
-Embeddings 
-Vector Store 
-LLM
"""

from typing import Dict, List 
from embeddings import EmbeddingGenerator
from vector_store import VectorStore 
from ollama_control import OllamaLLM

class QueryProcessor: 
    """
    Tie toegether the whole RAG pipline  
    """

    def __init__(
            self,
            collection_name: str, 
            embedding_model: str ='nomic-embed-text', 
            llm_model: str='llama3.2',
            chroma_persist_dir: str = "./chroma_db"

    ):
        """
        INIT Method 
        :Initialize the RAG pipeline components
        
        Args:
            collection_name: Which Chroma collection to query
            embedding_model: Model for embeddings
            llm_model: Model for answer generation
            chroma_persist_dir: Where Chroma DB is stored
        """
        print("Initializing RAG pipline...")

        #Initlialization
        self.embedder = EmbeddingGenerator(model_name=embedding_model)
        self.vector_store = VectorStore(persist_directory=chroma_persist_dir)
        self.vector_store.create_collection(collection_name)
        self.llm = OllamaLLM(model_name=llm_model)
        print('RAG Pipline Ready')

    def process_query (
            self,
            question: str, 
            top_k: int =5,
            include_metadata: bool = True
    )-> Dict:
        """
         Complete RAG pipeline: Question -> Answer

         This is the main method called by the Flask App

         Pipeline:
         1. Embed question
         2. Search vector store
         3. Get relevant chunks
         4. Send to LLM
         5. Return answer 

        Args:
            question: User's question
            top_k: How many context chunks to retrieve
            include_metadata: Whether to include debug info
        
        Returns:
            Dict with answer and metadata
        """
        print(f"\n{'='*60}")
        print(f"Processing Query: {question}")
        print('='*60)
        
        #Step 1: Embed the Model 
        print('\n[1/4] Embedding Question...')
        question_embedding = self.embedder.embed(question)
        print(f"       Generated {len(question_embedding)}-dim embedding")
        
        #Step 2: Search Vector Store
        print('\n[2/4] Searching Vector Store...')
        search_results = self.vector_store.search(
            query_embedding=question_embedding,
            top_k=top_k
        )
        documents = search_results['documents']
        metadatas = search_results['metadatas']
        distances = search_results['distances']
        print(f"       Retrieved {len(documents)} relevant chunks")

        print("\n Top Matches:")
        for i, (doc,dist) in enumerate(zip(documents[:3],distances[:3]),1):
            print(f"      {i}. [{dist:.4f}] {doc[:80]}...")

        if not documents:
            return {
                'question': question,
                'answer': "I couldn't find any relevant data to answer this question.",
                'context_used': [],
                'success': False
            }
        #Step 4: Generate answer using LLM 
        print("\n [3/4] Generating answer with LLM...")
        llm_result = self.llm.answer_question(
            question=question,
            context_chunks = documents
        )
        print("    Answer Generated")

        print("\n [4/4] Preparing Response...")

        response = {
            'question': question,
            'answer': llm_result['answer'],
            'success': True,
            'num_chunks_used': len(documents)
        }
        # Add metadata if requested
        if include_metadata:
            response['metadata'] = {
                'context_chunks': documents,
                'chunk_metadata': metadatas,
                'similarity_scores': distances,
                'top_k': top_k,
                'embedding_model': self.embedder.model_name,
                'llm_model': self.llm.model_name
            }
        print("     Done \n")
        return response 
    
    def get_stats(self) -> Dict:
        """Get statistics about the current collection"""
        return self.vector_store.get_collection_stats()

    def process_multiple_queries(
            self,
            questions: List[str], 
            top_k: int=5
    ) -> List[Dict]:
        """
        Process multiple questions at once

        useful for: 
        - Testing 
        - Batch processing 
        - Conversation history 
        """
        results = []
        print(f'\n Processing {len(questions)} questions...')

        for i, question in enumerate(questions,1):
            print(f"\n[Query {i}/{len(questions)}]")
            result = self.process_query(
                question=question,
                top_k=top_k,
                include_metadata=False
            )
            results.append(result)
        return results

def main():
    """
    Test the complete RAG pipeline
    
    Prerequisites:
    1. Run embeddings.py and vector_store.py first to create test collection
    2. Make sure Ollama is running
    """
    
    # Initialize query processor
    # Note: Using the test collection created by vector_store.py
    processor = QueryProcessor(
        collection_name="test_collection",
        chroma_persist_dir="./test_chroma_db"
    )
    
    # Show collection stats
    print("\n" + "="*60)
    print("Collection Stats:")
    print("="*60)
    stats = processor.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Test single query
    print("\n\n" + "="*60)
    print("TEST 1: Single Query")
    print("="*60)
    
    result = processor.process_query(
        question="Who lives in New York City?",
        top_k=3
    )
    
    print("\n" + "="*60)
    print("FINAL ANSWER:")
    print("="*60)
    print(f"Q: {result['question']}")
    print(f"A: {result['answer']}")
    
    # Test multiple queries
    print("\n\n" + "="*60)
    print("TEST 2: Multiple Queries")
    print("="*60)
    
    questions = [
        "What is the average age?",
        "List all the cities mentioned",
        "Who is the oldest person?"
    ]
    
    results = processor.process_multiple_queries(questions, top_k=5)
    
    print("\n" + "="*60)
    print("RESULTS:")
    print("="*60)
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Q: {result['question']}")
        print(f"   A: {result['answer']}")


if __name__ == "__main__":
    main()

