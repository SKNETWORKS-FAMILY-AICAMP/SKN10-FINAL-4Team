# Create your views here.
from django.shortcuts import render
from influencers.models import Influencer

def homepage(request):
    return render(request, 'home/homepage.html')

def landingpage(request):
    influencers = Influencer.objects.all()
    user = request.user
    return render(request, 'home/landingpage.html', {
        'influencers': influencers,
        'user': user,
    })