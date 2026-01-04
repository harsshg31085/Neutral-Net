from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.apps import apps
import json

def home_view(request):
    return render(request, 'index.html')

@method_decorator(csrf_exempt, name='dispatch')
class RealTimeAnalyzeView(View):    
    def post(self, request):
        try:
            data = json.loads(request.body)
            text = data.get('text', '')
            
            if not text.strip():
                return JsonResponse({
                    'text': '',
                    'highlighted_html': '',
                    'biases': [],
                    'score': 100,
                    'pronoun_stats': {},
                    'word_count': 0
                })
            
            api_config = apps.get_app_config('api')
            detector = api_config.detector
            
            if detector is None:
                from .utils.bias_detector import BiasDetector
                detector = BiasDetector()

            analysis = detector.analyze_text(text)
            
            return JsonResponse({
                'text': text,
                'highlighted_html': analysis['highlighted_text'],
                'biases': analysis['biases'],
                'score': analysis['overall_score'],
                'pronoun_stats': analysis['pronoun_stats'],
                'word_count': analysis['word_count'],
                'bias_data': analysis['bias_data']
            })
            
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'text': '',
                'highlighted_html': '',
                'biases': [],
                'score': 100
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class ApplySuggestionView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            original_text = data.get('original_text', '')
            bias_id = data.get('bias_id', '')
            replacement = data.get('replacement', '')
            
            return JsonResponse({
                'success': True,
                'message': 'Suggestion applied',
                'bias_id': bias_id,
                'replacement': replacement
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)