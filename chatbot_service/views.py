import json
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from .models import ChatHistory
from .utils import generate_response

@require_POST
def chat_view(request):
    try:
        data = json.loads(request.body)
        message = data.get('message', '')
        
        response_text = generate_response(message, request.user)
        
        # Save history if logged in or if we want to track stats
        # For guest, user is None
        user_instance = request.user if request.user.is_authenticated else None
        
        ChatHistory.objects.create(
            user=user_instance,
            message=message,
            response=response_text
        )
        
        return JsonResponse({'response': response_text})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
