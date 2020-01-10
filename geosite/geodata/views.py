from django.http import HttpResponse, JsonResponse
from .models import *
from collections import defaultdict

# Helpers
def collection(oo):
	""" From a list of objects, make a featurecollection geojson item 
	"""
	return '{{"type": "FeatureCollection","features": [{}]}}'.format(
		','.join([i.as_feature() for i in oo]))

def links(id):
    """ all links to and from an object
    """
    l0,l1 = Link.objects.filter(o0__id=id),Link.objects.filter(o1__id=id)
    return {'from':[(l.o1.name,l.o1.id,l.ltype) for l in l0],
            'to':[(l.o0.name,l.o0.id,l.ltype) for l in l1]}

def grouped_links(id):
    l0,l1 = Link.objects.filter(o0__id=id),Link.objects.filter(o1__id=id)
    a = defaultdict(list)
    for l in list(l0):
        a[l.ltype].append((l.o1.name,l.o1.id))
    for l in list(l1):
        a[l.ltype].append((l.o0.name,l.o0.id))

    linked_mbws= Link.objects.filter(o0__in=[i[1] for i in a['FLD']]).filter(ltype='MBW')
    if linked_mbws:
        a['MBW'] = list(set([(i.o1.name,i.o1.id) for i in linked_mbws]))
    return a

# Views
def index(request):
    return HttpResponse("Hallo allemaal: geodata app hier")

def fields(request):
    return HttpResponse("Geodata : fields endpoint")
	
def info_basic(request,id):
    o = Object.objects.get(id=id)
    result = {
        'name':o.name,
        'id':o.id,
        'type':o.otype,
        'info':{i.key:i.value for i in o.info_set.all()},
        'links':grouped_links(id)
    }
    return JsonResponse(result)

def info(request,id):
    o = Object.objects.get(id=id)

    result = {
        'name':o.name,
        'id':o.id,
        'type':o.otype,
        'info':{i.key:i.value for i in o.info_set.all()},
        'links':{}
    }

    ll = grouped_links(id)

    if o.otype=='field' and 'FLD' in ll:
        result['links'].update({'putten':ll['FLD']})

    if o.otype=='borehole' and 'FLD' in ll:
        result['info'].update({'veld':ll['FLD']})

    # result['info']['operator'] = ll['OPR']        
    result['links']['vergunning'] = ll['ULI']        
    result['links']['mb werken'] = ll['MBW']        



    return JsonResponse(result)







def objects(request,id):
    # o = Object.objects.get(id=id)

    bboxstr = request.GET['bbox']
    wsen = list(map(float,bboxstr.split(',')))
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