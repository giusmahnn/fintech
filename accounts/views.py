from django.shortcuts import render

# Create your views here.


def home(request):
    context = {}  # Add context variables here if needed
    return render(request, 'accounts/home.html', context)