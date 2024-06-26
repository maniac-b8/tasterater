import os
import uuid
import boto3
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.forms import UserCreationForm
from .yelp_api import search_businesses, get_business_details
from .models import Restaurant, Favorite, Review, Photo
from django.contrib.auth import login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

def home(request):
    results = []
    is_search = False
    businesses = []
    if 'term' in request.GET and 'location' in request.GET:
        term = request.GET['term']
        location = request.GET['location']
        sort_by = request.GET.get('sort_by', 'rating')
        is_search = True
        results = search_businesses(term, location)

        businesses = results.get('businesses', [])
        if sort_by == 'rating':
            businesses = sorted(businesses, key=lambda x: x.get('rating', 0), reverse=True)
        elif sort_by == 'term':
            businesses = sorted(businesses, key=lambda x: x.get('term', '').lower())
    else:
        location = 'San Francisco'  
        results = search_businesses(location=location)
        businesses = sorted(results.get('businesses', []), key=lambda x: x.get('rating', 0), reverse=True)[:10]

    page = request.GET.get('page', 1)
    paginator = Paginator(businesses, 10)

    try:
        businesses = paginator.page(page)
    except PageNotAnInteger:
        businesses = paginator.page(1)
    except EmptyPage:
        businesses = paginator.page(paginator.num_pages)

    return render(request, 'home.html', {
        'results': businesses,
        'is_search': is_search,
        'term': request.GET.get('term', ''),
        'location': request.GET.get('location', location),
        'sort_by': request.GET.get('sort_by', 'rating'),
    })

@login_required
def add_favorite(request, yelp_id):
    restaurant = Restaurant.objects.filter(yelp_id=yelp_id).first()
    if not restaurant:
        business = get_business_details(yelp_id)
        if business and 'name' in business and 'location' in business and 'rating' in business:
            restaurant = Restaurant.objects.create(
                yelp_id=yelp_id,
                name=business['name'],
                location=business['location']['address1'],
                rating=business['rating']
            )
        else:
            return render(request, 'home.html', {'error_message': 'Failed to retrieve restaurant details from Yelp.'})
    Favorite.objects.get_or_create(user=request.user, restaurant=restaurant)
    return redirect('home')

@login_required
def remove_favorite(request, yelp_id):
    restaurant = get_object_or_404(Restaurant, yelp_id=yelp_id)
    favorite = get_object_or_404(Favorite, user=request.user, restaurant=restaurant)
    favorite.delete()
    return redirect('user_profile', user_id=request.user.id)

@login_required
def restaurant_detail(request, yelp_id):
    try:
        restaurant = Restaurant.objects.get(yelp_id=yelp_id)
    except Restaurant.DoesNotExist:
        business = get_business_details(yelp_id)
        if business and 'name' in business and 'location' in business and 'rating' in business:
            restaurant = Restaurant.objects.create(
                yelp_id=yelp_id,
                name=business['name'],
                location=business['location']['address1'],
                rating=business['rating'],
                image_url=business.get('image_url')
            )
        else:
            return render(request, 'home.html', {'error_message': 'Failed to retrieve restaurant details from Yelp.'})
    reviews = Review.objects.filter(restaurant=restaurant)
    return render(request, 'restaurant_detail.html', {'restaurant': restaurant, 'reviews': reviews, 'range': range(1, 6)})

@login_required
def add_review(request, yelp_id):
    restaurant = Restaurant.objects.filter(yelp_id=yelp_id).first()
    if not restaurant:
        business = get_business_details(yelp_id)
        if business and 'name' in business and 'location' in business and 'rating' in business:
            restaurant = Restaurant.objects.create(
                yelp_id=yelp_id,
                name=business['name'],
                location=business['location']['address1'],
                rating=business['rating'],
                image_url=business.get('image_url')
            )
        else:
            return render(request, 'home.html', {'error_message': 'Failed to retrieve restaurant details from Yelp.'})
    if request.method == 'POST':
        text = request.POST['text']
        rating = request.POST['rating']
        photo_file = request.FILES.get('photo-file', None)
        
        review = Review.objects.create(user=request.user, restaurant=restaurant, text=text, rating=rating)
        
        if photo_file:
            s3 = boto3.client('s3')
            key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
            try:
                bucket = os.environ['S3_BUCKET']
                s3.upload_fileobj(photo_file, bucket, key)
                url = f"{os.environ['AWS_S3_BASE_URL']}{bucket}/{key}"
                Photo.objects.create(url=url, review=review)
            except Exception as e:
                print('An error occurred uploading file to S3')
                print(e)
        
        return redirect('restaurant_detail', yelp_id=restaurant.yelp_id)
    return render(request, 'add_review.html', {'restaurant': restaurant, 'range': range(1, 6)})

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    restaurant = review.restaurant
    
    if request.method == 'POST':
        review.text = request.POST['text']
        review.rating = request.POST['rating']
        review.save()
        
        photo_file = request.FILES.get('photo-file', None)
        if photo_file:
            s3 = boto3.client('s3')
            key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
            try:
                bucket = os.environ['S3_BUCKET']
                s3.upload_fileobj(photo_file, bucket, key)
                url = f"{os.environ['AWS_S3_BASE_URL']}{bucket}/{key}"
                Photo.objects.create(url=url, review=review)
            except Exception as e:
                print('An error occurred uploading file to S3')
                print(e)                 
        
        return redirect('edit_review', review_id=review.id)
    return render(request, 'edit_review.html', {'review': review, 'restaurant': restaurant,  'range': range(1, 6)})

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    review.delete()
    return redirect('user_profile', user_id=request.user.id)

@login_required
def user_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    favorites = Favorite.objects.filter(user=user)
    reviews = Review.objects.filter(user=user)
    return render(request, 'profile.html', {'profile_user': user, 'favorites': favorites, 'reviews': reviews, 'range': range(1, 6)})

@login_required
def delete_photo(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    review_id = photo.review.id
    if request.method == 'POST':
        photo.delete()
        return redirect('edit_review', review_id=review_id)

def signup(request):
    error_message = ''
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        else:
            error_message = 'Invalid sign up - try again'
    form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/signup.html', context)
