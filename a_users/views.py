from django.shortcuts import render
from django.http import HttpResponse
from a_reviews.models import Review
# Create your views here.

def userView(request):
    # get users reviews and feed to template

    user_reviews = Review.objects.filter(author=request.user).select_related('course').order_by('-review_date')

    context = {
        'reviews': user_reviews,
        'reviews_count': user_reviews.count(),
    }


    return render(request, 'a_users/user.html', context)

def termsView(request):
    return render(request, 'pages/terms.html')
