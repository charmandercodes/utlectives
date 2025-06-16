from django.shortcuts import redirect, render
from django.http import HttpResponse
from a_reviews.models import Review
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
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


def deleteUserView(request, review_id):
    review = Review.objects.get(id=review_id)

    if request.method == 'POST':
        review.delete()
        return redirect('user-page')
    
    return render(request, 'a_users/review_confirm_delete.html', {'review': review})



