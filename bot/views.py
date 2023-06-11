from django.http import HttpRequest, JsonResponse
from .models import Feedback
from django.core.files import File
from .utils import handle_uploaded_file, send_feedback_to_moderation
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def create_feedback(request: HttpRequest):
    media = None
    if request.FILES.get('media') is not None:
        name = handle_uploaded_file(request.FILES['media'], request.FILES['media'].name)
        f = open(name, "rb")
        media=File(f, name=name)
            

    feedback = Feedback(
        name=request.POST.get('name'),
        working_place=request.POST.get('working_place'),
        text=request.POST.get('text'),
        media=media
    )

    feedback.save()

    send_feedback_to_moderation(feedback)

    return JsonResponse({"status": "ok"})


def get_feedbacks(request: HttpRequest):
    feedback = Feedback.objects.filter(is_accepted=True).values()
    return JsonResponse(list(feedback), safe=False)
