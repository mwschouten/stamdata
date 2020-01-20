import json
from . import geobor
from django.core.management.base import BaseCommand,CommandError
from geodata.models import *

class Collect(object):
    def __init__(self,otype,source_text=''):
        self.otype = otype
        self.source_text = source_text
        self._data = {}
        self._source = None
        
    @property
    def source(self):
        if not self._source:
            self._source,_ = Source.objects.get_or_create(source_text=self.source_text)
        return self._source
        
    def get(self,x):
        if not x in self._data:
            try:
                self._data[x] = Object.objects.get(otype=self.otype,name=x)
                self.last_created = False
            except Object.DoesNotExist:
                self._data[x] = Object.objects.create(otype=self.otype,name=x,source=self.source)
                self.last_created = True
        return self._data[x]


class Command(BaseCommand):
    help = 'import geobor well data'

    def handle(self,*args,**options):

        P = geobor.Putten()

        F = Collect('field', source_text=P.filename)
        O = Collect('operator', source_text=P.filename)
        M = Collect('mijnbouwwerk', source_text=P.filename)
        B = Collect('borehole', source_text=P.filename)

        print('OK START')
        for put in P.boreholes:

            o = B.get(put.Boorgatcode)

            
            if B.last_created:
                o.jsontext = geobor.point2str(put.Longitude_WGS84,put.Latitude_WGS84)
                o.west = put.Longitude_WGS84
                o.south = put.Latitude_WGS84
                o.east = put.Longitude_WGS84
                o.north = put.Latitude_WGS84
                o.save()
                # print('  created borehole: ',o.name,o.west,o.south)

                Info.objects.bulk_create(
                        [Info( item=o,key=desc,value=getattr(put,fld)) 
                         for fld,desc in geobor.flds_tosave.items()])


                if put.Huidige_eigenaar:
                    Link.objects.create(o0=o,o1=O.get(put.Huidige_eigenaar),ltype='OPR')
    
                if put.Veld_Naam:
                    Link.objects.create(o0=o,o1=F.get(put.Veld_Naam),ltype='FLD')

                if put.Mijnbouwwerk_Naam:
                    mbw = M.get(put.Mijnbouwwerk_Naam)
                    if M.last_created:
                        mbw.jsontext = geobor.point2str(put.Longitude_WGS84,put.Latitude_WGS84)
                        mbw.west = put.Longitude_WGS84
                        mbw.south = put.Latitude_WGS84
                        mbw.east = put.Longitude_WGS84
                        mbw.north = put.Latitude_WGS84
                        mbw.save()

                    Link.objects.create(o0=o,o1=mbw,ltype='MBW')

            else: # CHECK INFO

                pass

            # # Check info
            # for k
            #     Info.objects.bulk_create(
            #         [Info(item=oo[d[2]],key=d[0],value=d[1]) for d in data['info']])
        # self.stdout.write('Created info')


