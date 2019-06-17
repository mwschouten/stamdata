import json

from django.core.management.base import BaseCommand,CommandError
from geodata.models import *


class Command(BaseCommand):
    help = 'import geo data'

    def handle(self,*args,**options):

        with open('nlogdata.json', 'r') as f:
            data = json.load(f)

        self.stdout.write(', '.join([i[0] for i in data['objects']]))
