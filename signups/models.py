from django.db import models
import datetime

# Create your models here.
class Driver(models.Model):
    name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField()
    unique_string = models.TextField(null=True, blank=True)
    order = models.IntegerField(null=True, blank=True)
    signup_time = models.DateTimeField(auto_now=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.email

class Fura(models.Model):
    driver = models.ForeignKey(Driver)
    date = models.DateField()
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    miliseconds = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return datetime.datetime.strftime(self.start_time, '%d.%m. %H:%M')

class EmailToSend(models.Model):
    driver = models.ForeignKey(Driver)
    time = models.DateTimeField()
    sent = models.BooleanField(default=False)
    
class Options(models.Model):
    driver = models.ForeignKey(Driver)
    option1 = models.BooleanField(default=False)
    option2 = models.BooleanField(default=False)
    option3 = models.BooleanField(default=False)