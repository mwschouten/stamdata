from django.http import HttpResponse, JsonResponse
from .models import *
from collections import defaultdict

# Helpers
def collection(oo):
	""" From a list of objects, make a featurecollection geojson item 
	"""
	return '{{"type": "FeatureCollection","features": [{}]}}'.format(
		','.join([i.as_feature() for i in oo if i.has_geometry]))

def links(id):
    """ all links to and from an object
    """
    l0,l1 = Link.objects.filter(o0__id=id),Link.objects.filter(o1__id=id)
    return {'from':[(l.o1.name,l.o1.id,l.ltype) for l in l0],
            'to':[(l.o0.name,l.o0.id,l.ltype) for l in l1]}

def grouped_links(id):
    l0,l1 = Link.objects.filter(o0__id=id),Link.objects.filter(o1__id=id)
    a = defaultdict(list)
    flds=[]
    for l in list(l0):
        a[l.ltype].append((l.o1.name,l.o1.id))
    for l in list(l1):
        a[l.ltype].append((l.o0.name,l.o0.id))
        # MBW in l1 meanse that we have a mbw, and want the fields behind wells too
        if l.ltype=='MBW':
            fld = l.o0.obj_from.get(ltype='FLD').o1
            flds.append((fld.name,fld.id))
    if not 'FLD' in a:
        a['FLD'] = list(set(flds))
    # The other way around: fields we want with mbw asl well, although this is through boreholes
    linked_mbws= Link.objects.filter(o0__in=[i[1] for i in a['FLD']]).filter(ltype='MBW')
    if linked_mbws:
        a['MBW'] = list(set([(i.o1.name,i.o1.id) for i in linked_mbws]))



    return a

# Views
def index(request):
    return HttpResponse("Hallo allemaal: geodata app hier")
	
def info(request,id):
    o = Object.objects.get(id=id)

    result = {
        'name':o.name,
        'id':o.id,
        'type':o.otype,
        'lalo':o.lalo,
        'info':{i.key:i.value for i in o.info_set.all()},
        'links':{}
    }
    ll = grouped_links(id)
    if not 'FLD' in ll:
        ll['FLD']='-'

    if o.otype=='field':
        result['links']['vergunning'] = ll['ULI']        
        result['links']['mb werken'] = ll['MBW']        
        result['links'].update({'putten':ll['FLD']})

    elif o.otype=='mijnbouwwerk':
        result['links']['putten'] = ll['MBW']
        result['links']['velden'] = ll['FLD']


    elif o.otype=='borehole':
        result['links']['field'] = ll['FLD']
        result['links']['mb werk'] = ll['MBW']


    return JsonResponse(result)


# def objects(request,id):
#     # o = Object.objects.get(id=id)

#     bboxstr = request.GET['bbox']
#     wsen = list(map(float,bboxstr.split(',')))
#     o = Object.objects.filter(west__lt=wsen[2],east__gt=wsen[0],
#                            south__lt=wsen[3],north__gt=wsen[1],otype='field')
#     print('Found objects : ',len(o))
#     return HttpResponse(collection(o))

def fields(request):
    o = Object.objects.filter(otype='field')
    return HttpResponse(collection(o))

def locations(request):
    oo = Object.objects.filter(otype='mijnbouwwerk')
    
    def safename(o):
        return o.name.replace('-',' ')

    result={safename(o):{'lat':float(o.north),'lng':float(o.west)} for o in oo}
    return JsonResponse(result)





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