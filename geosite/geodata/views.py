from django.http import HttpResponse

def index(request):
    return HttpResponse("Hallo allemaal: geodata app hier")

def fields(request):
    return HttpResponse("Geodata : fields endpoint")
	