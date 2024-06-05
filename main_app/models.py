from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Restaurant(models.Model):
    yelp_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    rating = models.FloatField()
    
    def __str__(self):
      return self.name    

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('user', 'restaurant') 
  
class Review(models.Model):
   user = models.ForeignKey(User, on_delete=models.CASCADE)
   restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
   text = models.TextField()
   rating = models.PositiveSmallIntegerField()
   
   
   class Meta:
       unique_together = ('user', 'restaurant')
       
   def __str__(self):
    return f"{self.user.username} - {self.restaurant.name}"    
      