from django.db import models
from users.models import User
from influencers.models import Influencer

# Create your models here.
class History(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    influencer = models.ForeignKey(Influencer, on_delete=models.CASCADE)
    history = models.JSONField(default=list, blank=True)