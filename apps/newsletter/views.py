import json
import logging
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST

logger = logging.getLogger(__name__)


@require_POST
def subscribe(request):
    """Subscribe email to Beehiiv newsletter."""
    email = request.POST.get('email', '').strip()
    
    if not email:
        return JsonResponse({
            "status": "error", 
            "message": "Email address is required."
        }, status=400)
    
    # Beehiiv API v2 endpoint
    api_key = getattr(settings, 'BEEHIIV_API_KEY', '')
    pub_id = getattr(settings, 'BEEHIIV_PUBLICATION_ID', '')
    
    if not api_key or not pub_id:
        logger.error("Beehiiv API credentials not configured")
        return JsonResponse({
            "status": "error",
            "message": "Newsletter service temporarily unavailable."
        }, status=500)
    
    # Beehiiv API v2 subscription endpoint
    url = f"https://api.beehiiv.com/v2/publications/{pub_id}/subscriptions"
    
    payload = {
        "email": email,
        "reactivate_existing": False,
        "send_welcome_email": True,
        "utm_source": "website",
        "utm_medium": "newsletter_form",
        "utm_campaign": "organic_signup"
    }
    
    try:
        # Prepare the request
        data = json.dumps(payload).encode('utf-8')
        req = Request(url, data=data, method='POST')
        req.add_header('Content-Type', 'application/json')
        req.add_header('Authorization', f'Bearer {api_key}')
        
        # Make the API call
        with urlopen(req, timeout=10) as response:
            if response.getcode() == 201:
                return JsonResponse({
                    "status": "ok",
                    "message": "Thanks for subscribing! Check your email to confirm."
                })
            else:
                logger.warning(f"Beehiiv API returned status {response.getcode()}")
                return JsonResponse({
                    "status": "error",
                    "message": "Unable to subscribe. Please try again."
                }, status=500)
                
    except HTTPError as e:
        if e.code == 400:
            # Bad request - possibly duplicate email
            response_data = json.loads(e.read().decode('utf-8'))
            if 'already subscribed' in str(response_data).lower():
                return JsonResponse({
                    "status": "ok",
                    "message": "You're already subscribed! Check your email for updates."
                })
        
        logger.error(f"Beehiiv API HTTP error: {e.code} - {e.reason}")
        return JsonResponse({
            "status": "error",
            "message": "Unable to subscribe. Please try again later."
        }, status=500)
        
    except URLError as e:
        logger.error(f"Beehiiv API connection error: {e.reason}")
        return JsonResponse({
            "status": "error",
            "message": "Connection error. Please check your internet and try again."
        }, status=500)
        
    except Exception as e:
        logger.error(f"Unexpected error in newsletter subscription: {str(e)}")
        return JsonResponse({
            "status": "error",
            "message": "Something went wrong. Please try again."
        }, status=500)
