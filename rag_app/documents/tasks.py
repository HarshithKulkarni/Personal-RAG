# documents/tasks.py
from celery import shared_task
from .models import Document
from .utils import extract_text_and_generate_embedding
from .models import DocumentEmbedding

@shared_task
def process_document(document_id):
    try:
        print("Fetching document from db")
        doc = Document.objects.get(id=document_id)

        chunks, embedding_vectors = extract_text_and_generate_embedding(doc)

        for chunk, emb in zip(chunks, embedding_vectors):
            print(f"Storing embedding for chunk: {chunk[:30]}... (vector length: {len(emb)})")
            # Create a new DocumentEmbedding record for each embedding vector
            DocumentEmbedding.objects.create(document=doc, embedding=emb)

    except Document.DoesNotExist:
        print("Document Does not Exist!!")