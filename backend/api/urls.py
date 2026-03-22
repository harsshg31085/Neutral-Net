from django.urls import path
from .views import RealTimeAnalyzeView, ApplySuggestionView, DocumentUploadView

urlpatterns = [
    path('real-time-analyze/', RealTimeAnalyzeView.as_view(), name='real-time-analyze'),
    path('apply-suggestion/', ApplySuggestionView.as_view(), name='apply-suggestion'),
    path('upload-document/', DocumentUploadView.as_view(), name='upload-document')
]