from django.urls import path
from .views import RealTimeAnalyzeView, ApplySuggestionView

urlpatterns = [
    path('real-time-analyze/', RealTimeAnalyzeView.as_view(), name='real-time-analyze'),
    path('apply-suggestion/', ApplySuggestionView.as_view(), name='apply-suggestion'),
]