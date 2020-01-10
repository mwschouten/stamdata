import json

from django.core.management.base import BaseCommand
from geodata.models import Source,Object,Link,Info


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

        # Create the objects
        def make_object(d):

            o = Object.objects.filter(name=d[0],otype=d[1])
            if o:
                return o[0]

            if d[3]:
                # 2-D object (area)
                # print(d)
                return Object.objects.create(source=s,
                                name = d[0],
                                otype=d[1],
                                jsontext=d[2],
                                west=d[3][0],
                                south=d[3][1],
                                east=d[3][2],
                                north=d[3][3])

            else:
                # 0-D object (non-geographic)
                return Object.objects.create(source=s,
                                    name = d[0],
                                    otype=d[1],
                                    jsontext=d[2])    



        # Objects refered to by number in this importfile
        reference_by_number = type(data['info'][0][2]) == int

        def key(d):
            return "{}_{}".format(d[0],d[1])

        if reference_by_number:
            oo_list = [make_object(d) for d in data['objects']]
            oo = {key(d):o for d,o in zip(data['objects'],oo_list)}

        # Objects refered to by name
        else:
            oo = {key(d):make_object(d) for d in data['objects']}

       
        self.stdout.write('Created {} objects'.format(len(oo)))
        # for i,o in enumerate(oo):
        #     self.stdout.write("{} : {} ({}) ({})".format(i,o.name,o.otype,data['objects'][i]))

        print('Number of info items : ',len(data['info']))


        if reference_by_number:
            # Objects refered to by number in this importfile
            Info.objects.bulk_create([Info(item=oo_list[d[2]],key=d[0],value=d[1]) 
                                        for d in data['info']])
        else:
            # Objects refered to by name
            Info.objects.bulk_create([Info(item=oo[d[2]],key=d[0],value=d[1]) 
                                        for d in data['info']])


        self.stdout.write('Created info')

        # Make sure we have all linked items (if they have names)
        # When the objects are numbered items, we have to assume all is right
        if not reference_by_number:
          for d in data['links']:
            print (d, ' -> ')
            if not d[0] in oo:
                raise Exception('Should not happen: info to non-existing object')
            if not d[1] in oo:

                if d[2]=='OPR':
                    oo[d[1]] = make_object([d[1],'operator','',None])

                if d[2]=='MBW':
                    new_object = oo[d[0]]
                    new_object.pk = None
                    new_object.otype='mijnbouwwerk'
                    new_object.save()
                    oo[d[1]] = new_object

                if d[2]=='FLD':
                    oo[d[1]] = make_object([d[1],'field','',None])


            print ('        ',oo[d[0]].name,oo[d[1]].name)

        if type(data['links'][0][0]) == int:
            # Objects refered to by number in this importfile
            Link.objects.bulk_create(
                [Link(o0=oo_list[d[0]],o1=oo_list[d[1]],ltype=d[2]) 
                 for d in data['links']])
        else:
            # Objects refered to by name
            Link.objects.bulk_create([Link(o0=oo[d[0]],o1=oo[d[1]],ltype=d[2]) 
                                        for d in data['links']])
        self.stdout.write('Created links')


