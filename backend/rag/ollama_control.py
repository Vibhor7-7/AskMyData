"""
Ollama Control Module 

What does it do? 
- Takes retrival context chunks 
- Constructs a prompt 
- Sends to Ollama LLM (llama3.2)
- Returns natural language answer 
"""

import ollama
from typing import List, Dict 

class OllamaLLM:
    """
    Manages communication with Ollama LLM
    """

    def __init__(self, model_name: str ="llama3.2"):
        """
        Initialize Ollama LLM

        Args:
            model_name: Name of Ollama model to use
                       Options: llama3.2, mistral, llama2, etc
        """
        self.model_name = model_name 

        try:
            test_response = self.generate("Hello")
            print(f" LLM model '{model_name}' loaded successfully!")
        except Exception as e:
            print(f" Error loading LLM: {e}")
            print("  Make sure Ollama is running: ollama serve")
            print(f"  And model is installed: ollama pull {model_name}")
            raise 

    def generate(self, prompt: str, stream: bool = False)->str:
        """
        Generate text using Ollama LLM
        
        Args:
            prompt: The complete prompt to send to LLM
            stream: If True, stream response (for real-time display)
        
        Returns:
            Generated text response
        """
        try:
            response = ollama.generate(
                model=self.model_name,
                prompt=prompt,
                stream=stream
            )
            
            if stream:
                # For now, just return the full response
                return response['response']
            else:
                return response['response']
                
        except Exception as e:
            print(f"Error generating response: {e}")
            return f"Error: Could not generate response. {str(e)}"

    def construct_prompt(
            self,
            question: str, 
            context_chunks: List[str], 
            prompt_template: str = None
    ) -> str: 
        """
        Build a prompt for the LLM using retrieved context
        
        Why is this important?
        - The prompt structure affects answer quality
        - Need to give clear instructions
        - Context must be formatted clearly
        - Question must be explicit
        
        Args:
            question: User's question
            context_chunks: List of relevant text chunks from vector store
            prompt_template: Custom template (optional)
        
        Returns:
            Complete prompt string
        """
        # Default prompt template
        if prompt_template is None:
            prompt_template = """You are a helpful data analyst assistant. Your job is to answer questions based ONLY on the provided data context.

DATA CONTEXT:
{context}

INSTRUCTIONS:
1. Answer the question using ONLY the information in the DATA CONTEXT above
2. If the answer cannot be determined from the context, say "I cannot answer this based on the provided data"
3. Be specific and cite relevant data points
4. If the question asks for calculations (average, sum, count), perform them accurately
5. Keep your answer concise and direct

QUESTION: {question}

ANSWER:"""
        
        # Format context chunks
        context_text = "\n".join([
            f"_ {chunk}" for chunk in context_chunks
        ])

        prompt = prompt_template.format(
            context=context_text, 
            question=question 
        )

        return prompt 
    
    def answer_question(
            self, 
            question: str, 
            context_chunks: List[str]
    )->Dict: 
        """
        Complete Q&A flow: construct prompt → generate answer
        
        This is the main method that will be used!!
        
        Args:
            question: User's question
            context_chunks: Relevant chunks from vector store
        
        Returns:
            Dict with:
            {
                'question': original question,
                'answer': LLM's answer,
                'context_used': chunks that were used,
                'prompt': the full prompt (for debugging)
            }
        """
        prompt = self.construct_prompt(question, context_chunks)
        answer = self.generate(prompt)

        return{
            'question': question, 
            'answer':answer.strip(),
            'context_used': context_chunks, 
            'num_context_chunks':len(context_chunks),
            'prompt':prompt # for debugging 
        }
def main():
    """ Test the file"""

    llm = OllamaLLM(model_name='llama3.2')

    sample_context = [
        "name: Alice, age: 25, city: NYC",
        "name: Bob, age: 30, city: LA",
        "name: Charlie, age: 35, city: Chicago"
    ]

    question = "What is the average age?"
    
    print("\n" + "="*60)
    print("Testing LLM Answer Generation")
    print("="*60)
    
    result = llm.answer_question(question, sample_context)
    
    print(f"\nQuestion: {result['question']}")
    print(f"\nContext used ({result['num_context_chunks']} chunks):")
    for i, chunk in enumerate(result['context_used'], 1):
        print(f"  {i}. {chunk}")
    
    print(f"\n{'='*60}")
    print("ANSWER:")
    print('='*60)
    print(result['answer'])
    
    # Test another question
    print("\n\n" + "="*60)
    question2 = "Who lives in Los Angeles?"
    result2 = llm.answer_question(question2, sample_context)
    
    print(f"Question: {result2['question']}")
    print(f"\nAnswer: {result2['answer']}")
    ...

if __name__ == '__main__':
    main()

