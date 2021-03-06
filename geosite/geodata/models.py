from django.db import models
from decimal import Decimal
# Create your models here.

class Source(models.Model):
    source_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published',auto_now_add=True)

    def __str__(self):
        return '{} {}'.format(self.source_text, self.pub_date.strftime('%D %T'))
    
class Object(models.Model):
    name = models.CharField(max_length=200)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    otype = models.CharField(max_length=20) 
    jsontext = models.TextField()
    west = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    east = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    south = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    north = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    @property
    def has_geometry(self):
        return self.north is not None
    

    @property
    def lalo(self):
        try:
            return float(self.south+self.north)*0.5,float(self.west+self.east)*0.5
        except:
            return None

    def as_feature(self):
        if self.north is None:
            return None
        lalo = "[{:.5f},{:.5f}]".format(*self.lalo)
        return '{{"type":"Feature","properties":{{"name":"{}","id":"{}","type":"{}","lalo":{}}},"geometry":{}}}'.format(
            self.name,self.id,self.otype,lalo,self.jsontext)        

    def __str__(self):
        return self.name

    class Meta:
        unique_together = [['name','otype']]


class Info(models.Model):
    item = models.ForeignKey(Object, on_delete=models.CASCADE)
    key = models.CharField(max_length=200)
    value = models.CharField(max_length=200)

class Link(models.Model):
    o0 = models.ForeignKey(Object, related_name='obj_from', on_delete=models.CASCADE)
    o1 = models.ForeignKey(Object, related_name='obj_to', on_delete=models.CASCADE)
    ltype = models.CharField(max_length=3)

    def __str__(self):
        return "{}  -- ({}) -> {}".format(self.o0.name,self.ltype,self.o1.name)



