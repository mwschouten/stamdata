from django.http import HttpResponse
from .models import *

# Helpers
def collection(oo):
	""" From a list of objects, make a featurecollection geojson item 
	"""
	return '{{"type": "FeatureCollection","features": [{}]}}'.format(
		','.join([i.as_feature() for i in oo]))

# Views
def index(request):
    return HttpResponse("Hallo allemaal: geodata app hier")

def fields(request):
    return HttpResponse("Geodata : fields endpoint")
	
def info(request,id):
    o = Object.objects.get(id=id)
    return JsonResponse(o.infolist())

def objects(request,id):
    # o = Object.objects.get(id=id)

    bboxstr = request.GET['bbox']
    wsen = list(map(float,bboxstr.split(',')))
    print ('AAP', wsen)

    o = Object.objects.filter(west__lt=wsen[2],east__gt=wsen[0],
    					   south__lt=wsen[3],north__gt=wsen[1],otype='field')

    print('Found objects : ',len(o))

    return HttpResponse(collection(o))






# {
#   "type": "FeatureCollection",
#   "features": [
#	{
#       "type": "Feature",
#       "geometry": {
#         "type": "Point",
#         "coordinates": [0, 0]
#       },
#       "properties": {
#         "name": "null island"
#       }
#     }
#   ]
# }