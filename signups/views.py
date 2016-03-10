# -*- coding: utf-8 -*-

from django.conf import settings
from django.shortcuts import render, render_to_response, redirect
from django.core.context_processors import csrf
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.core.mail import EmailMultiAlternatives
from django.utils import crypto

from signups.utils import getTimes
import signups.emails as emails
from signups.models import Driver, Fura, EmailToSend, Options

import datetime
from pytz import timezone

# Create your views here.
@require_http_methods(['POST'])
@csrf_protect
def signup(request):
    
    name = request.POST.get('name')
    last_name = request.POST.get('last_name')
    email = request.POST.get('email')
    option1 = request.POST.get('option1')
    option2 = request.POST.get('option2')
    option3 = request.POST.get('option3')
    
    if len(Driver.objects.filter(email=email)) > 0:
        return HttpResponse(0)
    
    times = getTimes()
    
    secret = crypto.get_random_string(length=32)
    
    novuser = Driver(
        name=name,
        last_name=last_name,
        email=email,
        start_time=times['start'],
        end_time=times['end'],
        unique_string=secret
    )
    novuser.save()
    
    novafura = Fura(driver=novuser, date=times['date'], start_time=times['start'], end_time=times['end'])
    novafura.save()

    if option1 == '1':
        option1 = True
    else:
        option1 = False
    
    if option2 == '1':
        option2 = True
    else:
        option2 = False
    
    if option3 == '1':
        option3 = True
    else:
        option3 = False
    
    noveoptions = Options(driver=novuser, option1=option1, option2=option2, option3=option3)
    noveoptions.save()
    
    # send first email
    msg = EmailMultiAlternatives(
        subject = emails.pozdravnimail['subject'],
        body = emails.parseContent(
            emails.pozdravnimail['content'],
            {
                'ime': name,
                'datum': datetime.datetime.strftime(novafura.start_time, '%d.%m.'),
                'ura': datetime.datetime.strftime(novafura.start_time, '%H:%M')
            }
        ),
        from_email = emails.pozdravnimail['sender'],
        to = [novuser.email],
        headers={
            'Reply-To': emails.pozdravnimail['sender']
        } # optional extra headers
    )
    
    msg.attach_alternative(emails.parseContent(
            emails.pozdravnimail['content'],
            {
                'ime': name,
                'datum': datetime.datetime.strftime(novafura.start_time, '%d.%m.'),
                'ura': datetime.datetime.strftime(novafura.start_time, '%H:%M'),
                'secret': secret
            }
        ),"text/html")


    # Send it:
    msg.send()
    print 'Email sent'
    
    # schedule email
    emailtosend = EmailToSend(
        driver=novuser,
        time=novafura.end_time - datetime.timedelta(minutes=15)
    )
    emailtosend.save()
    
    return HttpResponse(novuser.unique_string)

@csrf_protect
def index(request):
    c = {}
    c.update(csrf(request))
    
    return render_to_response('signup.html', c)

def stream(request):
    
    time = datetime.datetime.now()
#    tz = timezone(settings.TIME_ZONE)
#    time = time.replace(tzinfo = tz)
    
    isactive = False
    fura = None
    furas = Fura.objects.filter(start_time__lt=time).filter(end_time__gt=time)
    
    if len(furas) > 0:
        fura = furas[0]
        isactive = True
    
    c = {'fura': fura, 'isactive': isactive}
    c.update(csrf(request))
    
    return render_to_response('stream.html', c)

def drive(request, driversecret):
    
    # if no id redirect to stream
    if not driversecret:
        print 'No id'
        return redirect('/stream')
    
    # get driver queryset
    drivers = Driver.objects.filter(unique_string=driversecret)
    
    # if driver does not exist redirect to stream
    if len(drivers) < 1:
        print 'No driver in db'
        return redirect('/stream')
    
    driver = drivers[0]
    driverid = driver.id
    
    # if too soon or too late redirect to stream
    time = datetime.datetime.now()
#    tz = timezone(settings.TIME_ZONE)
#    time = time.replace(tzinfo = tz)

    start = driver.fura_set.all()[0].start_time
    end = driver.fura_set.all()[0].end_time

    if end <= time: # time < (start - datetime.timedelta(minutes=2)) or
        print 'Not the time'
        return redirect('/stream')
    
    c = {
        'driver': driver,
        'fura': driver.fura_set.all()[0]
    }
    
    c.update(csrf(request))
    
    return render_to_response('drive.html', c)

@csrf_exempt
def checkSecret(request):
    unique_string = request.POST.get('secret')
    
    driver = Driver.objects.filter(unique_string=unique_string)
    
    if len(driver) < 1:
        return HttpResponse(0)
    
    else:
        
        time = datetime.datetime.now()
#        tz = timezone(settings.TIME_ZONE)
#        time = time.replace(tzinfo = tz)
        
        start = driver[0].fura_set.all()[0].start_time
        end = driver[0].fura_set.all()[0].end_time
        
        if start <= time < end:
        
            return HttpResponse(1)
        
        else:
            
            return HttpResponse(0)

@csrf_exempt
def checkTime(request):
    fura = Fura.objects.filter(id=int(request.GET.get('fura')))
    
    if len(fura) < 1:
        return HttpResponse(0)
    else:
        time = datetime.datetime.now()
#        tz = timezone(settings.TIME_ZONE)
#        time = time.replace(tzinfo = tz)
        
        if fura[0].end_time <= time:
            return HttpResponse(0)
    
        if time <= fura[0].start_time:
            return HttpResponse(0)
        
    return HttpResponse(1)

def sendEmailReminder(request):
    emails.sendReminder()
    
    return HttpResponse(1)

def testDrive(request):
    return render_to_response('drive.html', {})

def listDriversandFuras(request):
    furas = Fura.objects.all().order_by('start_time').reverse();
    return render_to_response('list.html', {'furas': furas})

def getTime(request):
    
    furas = Fura.objects.filter(id=int(request.GET.get('fura')))
    
    if len(furas) < 1:
        return HttpResponse(0)
    else:
        fura = furas[0]
        time = datetime.datetime.now()
        
        diff = fura.end_time - time
        
        return HttpResponse(diff.total_seconds())