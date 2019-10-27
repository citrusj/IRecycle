
# Create your models here.
from django.conf import settings
from django.db import models
from django.utils import timezone


class Post(models.Model):
    image = models.ImageField(upload_to='images/')
    created_date = models.DateTimeField(default=timezone.now())
    category = models.CharField(max_length=200, blank=True)
    def __str__(self):
        return str(self.id)