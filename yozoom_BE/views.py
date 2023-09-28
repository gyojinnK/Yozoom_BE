from django.http import JsonResponse

def test_view(request):
    return JsonResponse({'message':'C.Bal!'})


