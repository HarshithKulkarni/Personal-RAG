from django.urls import path
from .views import DocumentIngestionView, QnAView, DocumentSelectionView

urlpatterns = [
    path('ingest/', DocumentIngestionView.as_view(), name='document-ingest'),
    path('query/', QnAView.as_view(), name='answer-query'),
    path("select-documents/", DocumentSelectionView.as_view(), name="select_documents"),
]
