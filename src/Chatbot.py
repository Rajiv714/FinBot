import os
from dotenv import load_dotenv
from embeddings.embeddings import create_embedding_service
from vectorstore.qdrant_client import create_qdrant_client
from llm.gemini import create_gemini_service

load_dotenv()

def run_chatbot():
    embedding_service = create_embedding_service()
    embedding_dim = embedding_service.get_embedding_dimension()
    gemini_service = create_gemini_service()
    vector_client = create_qdrant_client(vector_size=embedding_dim)

    print("Welcome to the FinBot Financial Assistant. Type 'exit' to quit.")
    
    while True:
        query = input("\nAsk a question: ")
        if query.lower() in ["exit", "quit"]:
            break

        # Search for relevant chunks
        try:
            # Get embeddings for the query
            query_embedding = embedding_service.encode([query])[0]
            
            # Search in vector database
            results = vector_client.search(
                query_embedding=query_embedding,
                limit=5,
                score_threshold=0.3
            )
            
            # Extract context from results
            context_docs = []
            for result in results:
                context_docs.append({
                    "text": result.get("text", ""),
                    "metadata": result.get("metadata", {})
                })
            
            # Generate response using context
            context_text = "\n".join([doc["text"] for doc in context_docs])
            answer = gemini_service.generate_response(query, context=context_text)
            
            print(f"\nBot: {answer}")
            
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Bot: I'm sorry, I encountered an error while processing your question.")

if __name__ == "__main__":
    run_chatbot()