from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

# Create your models here.
class Restaurant(models.Model):
    yelp_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    rating = models.FloatField()
    image_url = models.URLField(max_length=500, null=True, blank=True)
    
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
   created_at = models.DateTimeField(default=timezone.now)
   
   class Meta:
       unique_together = ('user', 'restaurant')
       
   def __str__(self):
    return f"{self.user.username} - {self.restaurant.name}"    

class Photo(models.Model):
  url = models.CharField(max_length=200)
  review = models.ForeignKey(Review, on_delete=models.CASCADE)

  def __str__(self):
     return f"Photo for review_id: {self.review_id} @{self.url}"      