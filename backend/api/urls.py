from django.urls import path
from . import views

urlpatterns = [
    path('real-time-analyze/', views.RealTimeAnalyzeView.as_view(), name='real_time_analyze'),
    path('apply-suggestion/', views.ApplySuggestionView.as_view(), name='apply_suggestion'),
]