from django.db import models


class History(models.Model):
    file_name = models.CharField(max_length=255)
    percent = models.IntegerField(default=0)
    book_id = models.CharField(max_length=255)
