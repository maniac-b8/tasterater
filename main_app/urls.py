from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/signup/', views.signup, name='signup'), 
    path('restaurant/<str:yelp_id>/', views.restaurant_detail, name='restaurant_detail'), 
    path('add_review/<str:yelp_id>/', views.add_review, name='add_review'), 
    path('edit_review/<int:review_id>/', views.edit_review, name='edit_review'), 
    path('delete_review/<int:review_id>/', views.delete_review, name='delete_review'), 
    path('add_favorite/<str:yelp_id>/', views.add_favorite, name='add_favorite'),
    path('remove_favorite/<str:yelp_id>/', views.remove_favorite, name='remove_favorite'),
    path('profile/', views.profile, name='profile'),
]
