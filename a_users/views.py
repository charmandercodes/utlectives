from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.


def basicView(request):
    return render(request, 'a_users/page.html')

def termsView(request):
    return render(request, 'pages/terms.html')
