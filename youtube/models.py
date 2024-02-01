from django.db import models


class Videos(models.Model):
    url = models.URLField(unique=False)
    audio = models.FileField(upload_to="audio", default='')
    spanish_text = models.TextField()
    speech = models.FileField(upload_to="speech", default='')
    thumbnail = models.FileField(upload_to="thumbnail", default='')
    ocr = models.TextField()

    def __str__(self):
        return self.url
