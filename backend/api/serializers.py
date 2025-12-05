from rest_framework import serializers
from typing import Dict, Any, List

class TextAnalysisSerializer(serializers.Serializer):
    text = serializers.CharField(required=True)
    
class BiasDetectionSerializer(serializers.Serializer):
    text = serializers.CharField()
    highlighted_text = serializers.CharField()
    biases = serializers.ListField()
    bias_count = serializers.IntegerField()
    overall_score = serializers.IntegerField()
    pronoun_stats = serializers.DictField()
    word_count = serializers.IntegerField()
    sentence_count = serializers.IntegerField()
    
class SuggestionSerializer(serializers.Serializer):
    bias_id = serializers.CharField(required=True)
    replacement = serializers.CharField(required=True)
    
class ApplySuggestionSerializer(serializers.Serializer):
    original_text = serializers.CharField(required=True)
    bias_id = serializers.CharField(required=True)
    replacement = serializers.CharField(required=True)