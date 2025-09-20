from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.core.cache import cache
import redis

@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """Endpoint de health check pour Render"""
    try:
        # Vérifier la base de données
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Vérifier le cache Redis
        cache.set('health_check', 'ok', 10)
        cache_result = cache.get('health_check')
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'ok',
            'cache': 'ok' if cache_result == 'ok' else 'error',
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=500)