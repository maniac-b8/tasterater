from django.contrib.auth.forms import UserCreationForm
from .yelp_api import search_businesses, get_business_details
from .models import Restaurant
from django.contrib.auth import login
from django.shortcuts import render, redirect

# Create your views here.

def home(request):
  if 'term' in request.GET and 'location' in request.GET:
    term = request.GET['term']
    location = request.GET['location']
    results = search_businesses(term, location)
    return render (request, 'home.html', {'results': results['businesses']})
  return render(request, 'home.html')

def signup(request):
  error_message = ''
  if request.method == 'POST':
    form = UserCreationForm(request.POST)
    if form.is_valid():
      user = form.save()
      login(request, user)
      return redirect('home')
    else : error_message = 'Invalid sign up - try again'
  form = UserCreationForm()
  context = {'form': form, 'error_message': error_message}
  return render(request, 'registration/signup.html', context)