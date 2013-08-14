from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import get_object_or_404, render, redirect

@login_required
def stateofnature(request):
	#room = get_object_or_404(Room, slug=slug)    
    return render(request, "playpolitics/stateofnature.html", locals())