from django.http import HttpRequest, JsonResponse
from .models import Feedback
from .utils import send_feedback_to_moderation
from django.views.decorators.csrf import csrf_exempt
import threading

@csrf_exempt
def create_feedback(request: HttpRequest):
    print(list(request.POST.items()))
    if request.POST.get('name') is None:
        return JsonResponse({"status": "tilda-ok"})

    feedback = Feedback(
        name=request.POST.get('name'),
        working_place=request.POST.get('working_place'),
        text=request.POST.get('text'),
        media=request.POST.get('media'),
    )

    feedback.save()

    threading.Thread(target=send_feedback_to_moderation, args=(feedback,)).start()

    return JsonResponse({"status": "ok"})


def get_feedbacks(request: HttpRequest):
    feedback = Feedback.objects.filter(is_accepted=True).values()
    return JsonResponse(list(feedback), safe=False)
