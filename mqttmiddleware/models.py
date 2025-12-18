from django.db import models

class Message(models.Model):
    timestamp = models.DateTimeField()
    in_topic = models.CharField(max_length=255)
    out_topic = models.CharField(max_length=255, null=True, blank=True)
    payload = models.TextField() # check usage if JSON or string
    qos = models.IntegerField()
    time_ms = models.FloatField()
    status = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.timestamp} - {self.in_topic}'

    class Meta:
        ordering = ['-timestamp']

class SensorConfig(models.Model):
    sensor_type = models.CharField(max_length=50, unique=True, help_text="e.g. 'temp' or 'hum'")
    threshold = models.FloatField(default=20.0)

    def __str__(self):
        return f"{self.sensor_type}: > {self.threshold}"
