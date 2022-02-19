from django.db import models

# Create your models here.


# Create your views here.
class RegisterUser(models.Model):
    # Creates user
    user = models.CharField(max_length=100, blank=False, default="")