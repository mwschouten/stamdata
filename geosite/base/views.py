from django.shortcuts import render

def index(request):
    return render(request, 'base/index.html')

def index2(request):
    return render(request, 'base/sidepanel.html')
    # return render(request, 'base/probeer.html')
