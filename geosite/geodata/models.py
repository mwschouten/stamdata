from django.db import models

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

    def __str__(self):
        return self.name

class Info(models.Model):
    item = models.ForeignKey(Object, on_delete=models.CASCADE)
    key = models.CharField(max_length=200)
    value = models.CharField(max_length=200)

class Link(models.Model):
    o0 = models.ForeignKey(Object, related_name='obj_from', on_delete=models.CASCADE)
    o1 = models.ForeignKey(Object, related_name='obj_to', on_delete=models.CASCADE)
    ltype = models.CharField(max_length=3)



