from django.shortcuts import render

from chamas.models import Chama

def is_user_chama_member(function):
    def wrap(request, *args, **kwargs):
        chama = Chama.objects.get(pk=kwargs['chama_id'])
        user = request.user
        if chama.member.filter(user=user).exists():
            return function(request, *args, **kwargs)
        else:
            return render(request, 'chamas/not_chama_member.html')
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap