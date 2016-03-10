from django.db import models
import datetime
from django.utils import crypto

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
    session_id = models.CharField(null=True, blank=True)
    
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

def setFileName(instance, filename):
    ext = filename.split('.')[-1]
    newname = crypto.get_random_string(length=6) + '.' + ext
    pathandnewname = '/root/static/uploads/' + newname
    
    return pathandnewname
    
class postedImage(models.Model):
    thetitle = models.CharField(max_length=255)
    theimage = models.ImageField(upload_to='/root/static/uploads/', blank=True, null=True, default=None)
    
    def publicimageurl(self):
        if self.theimage:
            return 'http://pelji.se/static/uploads/' + self.thetitle
        else:
            return ''

class ReplacingBattery(models.Model):
    status = models.BooleanField(default=False)
