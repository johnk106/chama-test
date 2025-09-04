from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


# Create your views here.

def Home(request):
    """Root view that redirects based on authentication status"""
    if request.user.is_authenticated:
        return redirect('my_goals')  # Redirect to goals dashboard
    else:
        return redirect('homepage')  # Redirect to landing page

def homepage(request):
    """Landing page for non-authenticated users"""
    return render(request, 'index2.html')


def term_conditions(request):
    return render(request, 'term_conditions.html')

def privacy_policies(request):
    return render(request, 'privacy_policy.html')
