from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('accounts/signup/', views.signup, name='signup'), 
    path('add_review/<str:yelp_id>/', views.add_review, name='add_review'), 
    path('edit_review/<int:review_id>/', views.edit_review, name='edit_review'), 
    path('delete_review/<int:review_id>/', views.delete_review, name='delete_review'), 
]
