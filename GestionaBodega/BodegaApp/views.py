from django.shortcuts import render, redirect


# Create your views here.

def login(request):
    return render(request, 'web/login.html')

def inicio(request):
    return render(request, 'web/home.html')