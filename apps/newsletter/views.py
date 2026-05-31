from django.http import JsonResponse
from django.views.decorators.http import require_POST


@require_POST
def subscribe(request):
    """Stub endpoint for Beehiiv newsletter subscription."""
    # TODO: Integrate with Beehiiv API
    return JsonResponse(
        {"status": "ok", "message": "Newsletter integration coming soon."}
    )
