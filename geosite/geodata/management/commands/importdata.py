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
        s,created = Source.objects.get_or_create(source_text=source_text)
        if not created:
        	# remove all old, create new version of source item
            oo = Object.objects.filter(source=s).delete()
            s = Source.objects.create(source_text=source_text)

        with open(options['filename'], 'r') as f:
            data = json.load(f)
        # self.stdout.write(', '.join([i[0] for i in data['objects']]))

        for i in data['objects']:
        	Object.objects.create(source=s,
        		name = i[0],
        		otype=i[1],
        		jsontext=i[2])
