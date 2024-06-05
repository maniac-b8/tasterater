from django.db import models

# Create your models here.
class Restaurant(models.Model):
    yelp_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    rating = models.FloatField()
    
    def __str__(self):
      return self.name    