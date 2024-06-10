from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.forms import UserCreationForm
from .yelp_api import search_businesses, get_business_details
from .models import Restaurant, Favorite, Review
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

    # split pages
    page = request.GET.get('page', 1)
    paginator = Paginator(businesses, 10)  # show 10 businesses per page

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
        Review.objects.create(user=request.user, restaurant=restaurant, text=text, rating=rating)
        return redirect('home')
    return render(request, 'add_review.html', {'restaurant': restaurant, 'range': range(1, 6)})

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.method == 'POST':
        review.text = request.POST['text']
        review.rating = request.POST['rating']
        review.save()
        return redirect('user_profile', user_id=request.user.id)
    return render(request, 'edit_review.html', {'review': review,  'range': range(1, 6)})

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
