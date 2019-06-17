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
    jsontext = models.TextField()

    def __str__(self):
        return self.name




