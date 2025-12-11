from django.db import models

class Message(models.Model):
    timestamp = models.DateTimeField()
    in_topic = models.CharField(max_length=255)
    out_topic = models.CharField(max_length=255, null=True, blank=True)
    payload = models.TextField() # check usage if JSON or string
    qos = models.IntegerField()
    time_ms = models.FloatField()
    status = models.CharField(max_length=50)

    class Meta:
        ordering = ['-timestamp']
