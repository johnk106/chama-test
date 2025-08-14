from authentication.models import Profile


def user_profile(request):
	if request.user.is_authenticated:
		try:
			return {'user_profile': Profile.objects.get(owner=request.user)}
		except Profile.DoesNotExist:
			return {'user_profile': None}
	return {'user_profile': None}