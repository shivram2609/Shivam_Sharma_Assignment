from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from django.contrib.auth.models import AbstractUser

User = get_user_model()

class UserProfile(models.Model):
    """
    User Profile model associated 
    with auth User model. 

    """
    user = models.OneToOneField(User,related_name='profile', on_delete=models.CASCADE,null=True)
    gender = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=30, blank=True)
    city = models.CharField(max_length=20,null=True, blank=True)
    age = models.CharField(max_length=20,null=True, blank=True)


class Sales(models.Model):
    """
    Sales model.
    
    """
    class Meta:
        db_table = "user_sales"

    product= models.CharField(max_length=30)
    revenue = models.IntegerField()
    sales_number = models.IntegerField()
    sales_date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True)

    def __str__(self):
        return self.product


class Countries(models.Model):
    """
    Countries model.
    """
    class Meta:
        db_table = "countries"

    name= models.CharField(max_length=30)

    def __str__(self):
        return self.name

class Cities(models.Model):
    """
    cities model.
    """
    class Meta:
        db_table = "cities"
    
    name= models.CharField(max_length=30)
    countries = models.ForeignKey(Countries, on_delete=models.CASCADE,related_name='cities',null=True)
    
    def __str__(self):
        return self.name