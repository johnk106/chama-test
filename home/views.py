from django.shortcuts import render


# Create your views here.

def Home(request):
    return render(request, 'index.html')


def term_conditions(request):
    return render(request, 'term_conditions.html')

def privacy_policies(request):
    return render(request, 'privacy_policy.html')
