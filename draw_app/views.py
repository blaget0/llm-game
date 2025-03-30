from django.shortcuts import render

# Create your views here.

def drawer(request):
    return render(request, 'drawer.html')