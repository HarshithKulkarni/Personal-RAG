from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain.schema import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

def extract_text_and_generate_embedding(document: str, chunk_size: int = 200, chunk_overlap: int = 50):

    text = document.content
    processed_text = " ".join(text.split())

    text_splitter = RecursiveCharacterTextSplitter(
        # Set a really small chunk size, just to show.
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False,
    )

    chunks = text_splitter.split_text(processed_text)
    
    # Generate embeddings using the SentenceTransformer model via LangChain
    embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    embeddings = embedding_model.embed_documents(chunks)
    
    return chunks, embeddings


def re_rank_contexts(query, contexts):
    """
    Use the LLM to score each context for relevance to the query.
    Returns the contexts re-sorted by descending relevance.
    """

    llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash", 
            temperature=0, 
            max_tokens=50, 
            timeout=None, 
            max_retries=2
        )

    scored_contexts = []
    for context in contexts:
        # Define a re-ranking prompt based on open-source RAG ideas.
        prompt = (
            "Evaluate the relevance of the following context to the query. "
            "Rate its relevance on a scale from 1 (not relevant) to 10 (highly relevant). "
            "Provide only the numerical rating.\n\n"
            f"Context:\n{context}\n\n"
            f"Query:\n{query}\n\n"
            "Rating:"
        )
        messages = [HumanMessage(content=prompt)]
        response = llm(messages)
        try:
            print(response)
            score = float(response.strip())
        except Exception as e:
            score = 0.0
        scored_contexts.append((score, context))
    
    # Sort by descending score (highest relevance first)
    scored_contexts.sort(key=lambda x: x[0], reverse=True)

    return [ctx for score, ctx in scored_contexts]