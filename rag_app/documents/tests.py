from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Document, DocumentEmbedding
from django.contrib.auth.models import User
import numpy as np
import json

class DocumentViewsTestCase(TestCase):
    def setUp(self):
        """Set up test data before running each test"""
        self.client = APIClient()
        # self.user = User.objects.create_user(username="testuser", password="password123")
        # self.client.force_authenticate(user=self.user)

        # Create sample documents
        self.doc1 = Document.objects.create(title="Deep Learning Basics", content="Intro to deep learning", file_name="doc1.pdf")
        self.doc2 = Document.objects.create(title="AI Fundamentals", content="Intro to AI", file_name="doc2.pdf")
        
        # Create embeddings
        embedding1 = list(np.random.rand(384).astype(float))
        embedding2 = list(np.random.rand(384).astype(float))
        DocumentEmbedding.objects.create(document=self.doc1, embedding=embedding1)
        DocumentEmbedding.objects.create(document=self.doc2, embedding=embedding2)

    # --- Document Ingestion Tests ---

    def test_upload_single_pdf(self):
        """Test uploading a single valid PDF"""
        pdf_file = SimpleUploadedFile("test.pdf", b"Dummy PDF content", content_type="application/pdf")
        response = self.client.post('/api/documents/upload/', {'title': 'Test PDF', 'files': [pdf_file]})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_upload_multiple_pdfs(self):
        """Test uploading multiple valid PDFs"""
        pdf_file1 = SimpleUploadedFile("test1.pdf", b"Dummy PDF content 1", content_type="application/pdf")
        pdf_file2 = SimpleUploadedFile("test2.pdf", b"Dummy PDF content 2", content_type="application/pdf")
        response = self.client.post('/api/documents/upload/', {'title': 'Multiple PDFs', 'files': [pdf_file1, pdf_file2]})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_upload_non_pdf_file(self):
        """Test uploading a non-PDF file"""
        txt_file = SimpleUploadedFile("test.txt", b"Dummy text content", content_type="text/plain")
        response = self.client.post('/api/documents/upload/', {'title': 'Invalid File', 'files': [txt_file]})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_empty_files(self):
        """Test uploading with no files"""
        response = self.client.post('/api/documents/upload/', {'title': 'No Files'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_missing_title(self):
        """Test uploading without a title"""
        pdf_file = SimpleUploadedFile("test.pdf", b"Dummy PDF content", content_type="application/pdf")
        response = self.client.post('/api/documents/upload/', {'files': [pdf_file]})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_upload_large_pdf(self):
        """Test uploading a very large PDF file"""
        large_pdf = SimpleUploadedFile("large.pdf", b"A" * 10**6, content_type="application/pdf")
        response = self.client.post('/api/documents/upload/', {'title': 'Large PDF', 'files': [large_pdf]})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # --- QnA View Tests ---

    def test_qna_query_with_existing_title(self):
        """Test querying with an existing title"""
        response = self.client.post('/api/documents/query/', {'query': 'What is deep learning?', 'title': 'Deep Learning Basics'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('answer', response.data)

    def test_qna_query_with_non_existing_title(self):
        """Test querying with a non-existing title"""
        response = self.client.post('/api/documents/query/', {'query': 'What is AI?', 'title': 'Nonexistent Title'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_qna_query_without_title(self):
        """Test querying without a title"""
        response = self.client.post('/api/documents/query/', {'query': 'What is AI?'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_qna_empty_query(self):
        """Test querying with an empty query"""
        response = self.client.post('/api/documents/query/', {'query': ''})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_qna_no_query_param(self):
        """Test querying without the query parameter"""
        response = self.client.post('/api/documents/query/', {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_qna_large_query(self):
        """Test querying with a very large query"""
        large_query = "What is" + " A" * 1000
        response = self.client.post('/api/documents/query/', {'query': large_query})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # --- Document Selection View Tests ---

    def test_select_documents_by_title(self):
        """Test selecting documents by title and redirecting to QnAView"""
        response = self.client.post('/api/documents/select-documents/', {'title': 'Deep Learning Basics', 'query': 'Explain neural networks.'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_select_documents_non_existent_title(self):
        """Test selecting documents with a non-existent title"""
        response = self.client.post('/api/documents/select-documents/', {'title': 'Nonexistent', 'query': 'What is AI?'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_select_documents_empty_title(self):
        """Test selecting documents with an empty title"""
        response = self.client.post('/api/documents/select-documents/', {'title': '', 'query': 'What is deep learning?'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_select_documents_empty_query(self):
        """Test selecting documents with an empty query"""
        response = self.client.post('/api/documents/select-documents/', {'title': 'Deep Learning Basics', 'query': ''})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_select_documents_no_title_query(self):
        """Test selecting documents without title and query"""
        response = self.client.post('/api/documents/select-documents/', {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_select_documents_multiple_times(self):
        """Test selecting the same document multiple times"""
        self.client.post('/api/documents/select-documents/', {'title': 'Deep Learning Basics', 'query': 'Explain neural networks.'})
        response = self.client.post('/api/documents/select-documents/', {'title': 'Deep Learning Basics', 'query': 'Explain neural networks.'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
