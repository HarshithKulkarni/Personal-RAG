# documents/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Document, DocumentEmbedding
from .serializers import DocumentSerializer
from .tasks import process_document
from .utils import re_rank_contexts
from langchain_huggingface import HuggingFaceEmbeddings
import pdfplumber
from django.db.models.expressions import RawSQL
from langchain.llms import Ollama
# from langchain.vectorstores.pgvector import PGVector
from langchain_community.vectorstores import PGVector
from langchain.chains import RetrievalQA
from rag_app import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain.schema import HumanMessage


load_dotenv()

class DocumentIngestionView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
        # Retrieve the list of uploaded files   
        title = request.data.get('title')
        files = request.FILES.getlist('files')
        if not files:
            return Response({"error": "No files provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Retrieve the list of titles. 
        # Ensure your client sends the 'title' field multiple times for each file.

        created_docs = []
        errors = []

        # Process each file and assign the corresponding title by index
        for i, file_obj in enumerate(files):
            # Validate file type (only PDF allowed)
            if file_obj.content_type != 'application/pdf':
                errors.append(f"File '{file_obj.name}' is not a PDF.")
                continue

            # Extract text from the PDF using pdfplumber
            try:
                extracted_text = ""
                with pdfplumber.open(file_obj) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            extracted_text += page_text + "\n"
            except Exception as e:
                errors.append(f"Error processing file '{file_obj.name}': {e}")
                continue

            # If a title is provided for this file, use it; otherwise, use the file name
            file_name = file_obj.name

            # Create a Document instance with the extracted content
            doc = Document.objects.create(file_name=file_name, title=title, content=extracted_text)
            created_docs.append(doc)
            
            # Trigger asynchronous task to generate embeddings for this document
            process_document.delay(doc.id)
        
        serializer = DocumentSerializer(created_docs, many=True)
        response_data = {"documents": serializer.data}
        if errors:
            response_data["errors"] = errors
        
        return Response(response_data, status=status.HTTP_201_CREATED)


class QnAView(APIView):
    def post(self, request, format=None):
        query = request.data.get('query')
        # Optional: a category parameter to filter documents
        if('title' in request.data):
            title = request.data.get('title')
        else:
            title = None

        if not query:
            return Response({"error": "Query is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Use the same embedding model that was used during ingestion.
        embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # Generate an embedding for the query.
        query_embedding = embedding_model.embed_query(query)  # e.g. returns a list of 384 floats
        
        # Filter embeddings by category if provided.
        qs = DocumentEmbedding.objects.all()

        if title:
            qs = qs.filter(document__title__icontains=title)

        # Compute distances using pgvector's <-> operator
        relevant_embeddings = qs.annotate(
            distance=RawSQL("embedding <-> %s::vector", (query_embedding,))
        ).order_by("distance")[:5]
        
        # Gather context from the most relevant documents.
        contexts = [emb.document.content for emb in relevant_embeddings]

        # context_text = "\n\n".join(contexts)

        # Re-rank the contexts using the LLM scoring.
        reranked_contexts = re_rank_contexts(query, contexts)[:3]
        context_text = "\n\n".join(reranked_contexts)
        
        prompt = (
            "You are an expert assistant. Using only the context provided below, answer the query precisely. "
            "If the context does not contain enough information, respond with 'I do not have enough information to answer this question.'\n\n"
            f"Context:\n{context_text}\n\n"
            f"Query: {query}\n\n"
            "Answer:"
        )


        # Instantiate the LLM (using Google Gemini Flash in this case).
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash", 
            temperature=0, 
            max_tokens=None, 
            timeout=None, 
            max_retries=2
        )
        messages = [HumanMessage(content=prompt)]
        answer = llm(messages)
        
        return Response({
            "query": query,
            "title": title,
            "answer": answer
        }, status=status.HTTP_200_OK)