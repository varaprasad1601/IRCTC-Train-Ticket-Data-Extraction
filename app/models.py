from django.db import models
from django.contrib.auth.models import User


# Create your models here.
    
class user_details(models.Model):
    text = models.CharField(max_length=250,blank=True,null=True)
    

class user_info(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    wplace = models.CharField(max_length=250,blank=True,null=True)
    state = models.CharField(max_length=250,blank=True,null=True)
    mobile = models.CharField(max_length=250,blank=True,null=True)
    otp = models.CharField(max_length=250,blank=True,null=True)
    added_on = models.DateTimeField(auto_now_add=True,null=True)
    updated_on = models.DateTimeField(auto_now=True,null=True)


    def __str__(self):
        return self.user.username
    
    class Meta:
        verbose_name_plural = "Register Table"
        
class contact_us(models.Model):
    email = models.CharField(max_length=250,blank=True,null=True)
    subject = models.CharField(max_length=250,blank=True,null=True)
    message = models.TextField(blank=True,null=True)
    status = models.BooleanField(default=False)
    added_on = models.DateTimeField(auto_now_add=True,null=True)
    updated_on = models.DateTimeField(auto_now=True,null=True)
    
    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name_plural = "Contact Us Table"