import json

from django.core.management.base import BaseCommand,CommandError
from geodata.models import *


class Command(BaseCommand):
    help = 'import geo data'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('--filename',default='nlogdata.json')
        parser.add_argument('--description',default="")


    def handle(self,*args,**options):
        self.stdout.write('OPTIONS {}'.format(options))

        # Source item
        source_text = options['description'] or options['filename']
        ss = Source.objects.filter(source_text=source_text)
        for s in ss:
            # remove all old, create new version of source item
            oo = Object.objects.filter(source=s).delete()
        s = Source.objects.create(source_text=source_text)

        with open(options['filename'], 'r') as f:
            data = json.load(f)
        # self.stdout.write(', '.join([i[0] for i in data['objects']]))

        # Create the objects

        def make_object(d):
            if d[3]:
                return Object.objects.create(source=s,
                                    name = d[0],
                                    otype=d[1],
                                    jsontext=d[2],
                                    west=d[3][0],
                                    south=d[3][1],
                                    east=d[3][2],
                                    north=d[3][3],
                                    )
            else:
                return Object.objects.create(source=s,
                                    name = d[0],
                                    otype=d[1],
                                    jsontext=d[2])    


        oo = [make_object(d) for d in data['objects']]
    
        self.stdout.write('Created {} objects'.format(len(oo)))
        # for i,o in enumerate(oo):
        #     self.stdout.write("{} : {} ({}) ({})".format(i,o.name,o.otype,data['objects'][i]))


        Info.objects.bulk_create([Info(item=oo[d[2]],key=d[0],value=d[1]) 
                                        for d in data['info']])
        self.stdout.write('Created info')


        Link.objects.bulk_create([Link(o0=oo[d[0]],o1=oo[d[1]],ltype=d[2]) 
                                        for d in data['links']])
        self.stdout.write('Created links')


