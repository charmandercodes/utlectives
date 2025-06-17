from django.shortcuts import redirect, render
from django.http import HttpResponse
from a_reviews.models import Review
from django.contrib.auth.decorators import login_required
from a_reviews.forms import ReviewForm
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

def update_users_review(request, review_id):
    # get the review with the id we specified in the url for updating
    review = Review.objects.get(id=review_id)
    course = review.course  # Get the course from the review
    
    # instantiate the form with the review object data
    form = ReviewForm(instance=review)

    # if the request is post, then feed the form with the request data using the instance of the review object
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            # save the form
            form.save()
            return redirect('user-page')

    # pass both form and course to the template
    return render(request, 'a_reviews/review_form.html', {
        'form': form, 
        'course': course,
        'is_update': True  # Optional flag to differentiate between create/update
    })



