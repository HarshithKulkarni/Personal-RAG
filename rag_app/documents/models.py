from django.db import models
from pgvector.django import VectorField

class Document(models.Model):

    title = models.CharField(max_length=255)
    file_name = models.CharField(max_length=255)
    content = models.TextField()  # Raw text extracted from file
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class DocumentEmbedding(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='embeddings')
    embedding = VectorField(dimensions=384)  # Adjust dimensions as needed
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Embedding for {self.document.title}'
