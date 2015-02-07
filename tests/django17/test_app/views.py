from django.http import HttpResponse


def index(request):
    assert 1 == 2

    return HttpResponse('ok')
