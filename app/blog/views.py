from django.http import JsonResponse


def posts(request):
    data = [
            {
                "title": "Top 10 datasets"
            }
    ]

    return JsonResponse({"posts": data})
