# -*- coding: utf-8 -*-

from django.conf import settings
from django.shortcuts import render, render_to_response, redirect
from django.core.context_processors import csrf
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseServerError
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.core.mail import EmailMultiAlternatives
from django.utils import crypto
from django import forms
from django.views.decorators.cache import never_cache
from django.core.files.uploadedfile import InMemoryUploadedFile

from narodna.utils import getTimes
import narodna.emails as emails
from narodna.models import Driver, Fura, EmailToSend, Options, postedImage, ReplacingBattery

import StringIO
import datetime
import urllib
import io
import cStringIO
from PIL import Image
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
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

    # stopped generating furas TODO uncomment to make it work again CHANGED
    # novafura = Fura(driver=novuser, date=times['date'], start_time=times['start'], end_time=times['end'])
    # novafura.save()

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

    # send first email TODO CHANGED
    #msg = EmailMultiAlternatives(
    #    subject = emails.pozdravnimail['subject'],
    #    body = emails.parseContent(
    #        emails.pozdravnimail['content'],
    #        {
    #            'ime': name,
    #            'datum': datetime.datetime.strftime(novafura.start_time, '%d.%m.'),
    #            'ura': datetime.datetime.strftime(novafura.start_time, '%H:%M')
    #        }
    #    ),
    #    from_email = emails.pozdravnimail['sender'],
    #    to = [novuser.email],
    #    headers={
    #        'Reply-To': emails.pozdravnimail['sender']
    #    } # optional extra headers
    #)

    #msg.attach_alternative(emails.parseContent(
    #        emails.pozdravnimail['content'],
    #        {
    #            'ime': name,
    #            'datum': datetime.datetime.strftime(novafura.start_time, '%d.%m.'),
    #            'ura': datetime.datetime.strftime(novafura.start_time, '%H:%M'),
    #            'secret': secret
    #        }
    #    ),"text/html")


    # Send it: TODO CHANGED
    #msg.send()
    #print 'Email sent'

    # schedule email TODO CHANGED
    #emailtosend = EmailToSend(
    #    driver=novuser,
    #    time=novafura.end_time - datetime.timedelta(minutes=15)
    #)
    #emailtosend.save()

    return HttpResponse(novuser.unique_string)

@csrf_protect
def index(request):
    spots = getSpots()

    print spots

    spaceleft = True
    if spots == 'Na žalost so vsa mesta zasedena. Postavi se v čakalno vrsto in obvestili te bomo takoj, ko se kakšno mesto sprosti.':
        spaceleft = False

    c = {'spots': spots, 'spaceleft': spaceleft}
    c.update(csrf(request))

    return render_to_response('narodna/signup.html', c)

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

    return render_to_response('narodna/stream.html', c)

def drive(request, driversecret):

    print 'started drive'

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
    
    fura = driver.fura_set.all()[0]

    #Prevent that same fura opens by more people
    """if fura.session_id == "":
        fura.session_id = request.session._get_or_create_session_key()
        fura.save()
        request.session["id"] = fura.session_id
    elif fura.session_id != request.session.get("id"):
        return redirect('/signup')"""

    #Prevent that same fura opens by more people COOKIES
    cookie_for_set = False
    if fura.session_id == "" or fura.session_id == None:
        print "write cookie"
        fura.session_id = request.session._get_or_create_session_key()
        fura.save()
        cookie_for_set = True
        #prepare cookie data
        cookie = {"key": "fura_id","value": fura.session_id,"expires": fura.end_time}
    elif request.COOKIES.has_key('fura_id'):
        print "cookie je"
        if request.COOKIES['fura_id'] != fura.session_id:
            return redirect('/signup')
    else:
        return redirect('/signup')



    start = fura.start_time
    end = fura.end_time

    print 'testing time'

    if end <= time: # time < (start - datetime.timedelta(minutes=2)) or
        print 'Not the time'
        print end
        print time
        print driver.fura_set.all()[0].id
        return redirect('/stream')

    print 'tested time'

    c = {
        'driver': driver,
        'fura': driver.fura_set.all()[0]
    }

    c.update(csrf(request))

    print 'rendering narodna/drive.html'
    response = render_to_response('narodna/drive.html', c)
    if cookie_for_set:
        response.set_cookie(**cookie)
    return response

@csrf_exempt
def checkSecret(request):
    unique_string = request.POST.get('secret')

    driver = Driver.objects.filter(unique_string=unique_string)

    if ReplacingBattery.objects.all()[0].status:
        return HttpResponse(0)

    if unique_string == '1234567890':
        return HttpResponse(1)

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
        print 'no fura found'
        return HttpResponse(0)
    else:
        time = datetime.datetime.now()
#        tz = timezone(settings.TIME_ZONE)
#        time = time.replace(tzinfo = tz)

        if fura[0].end_time <= time:
            print 'too late'
            return HttpResponse(0)

        if time <= fura[0].start_time:
            print 'too soon'
            return HttpResponse(0)

    return HttpResponse(1)

def sendEmailReminder(request):
    emails.sendReminder()

    return HttpResponse(1)

def testDrive(request):
    c = {}
    c.update(csrf(request))
    return render_to_response('narodna/drive2.html', c)

def listDriversandFuras(request):
    furas = Fura.objects.all().order_by('start_time').reverse();
    return render_to_response('list.html', {'furas': furas})

def getTime(request):

    furas = Fura.objects.filter(id=int(request.GET.get('fura')))

    if len(furas) < 1:
        print 'no fura found'
        return HttpResponse(0)
    else:
        print 'checking fura'
        fura = furas[0]
        time = datetime.datetime.now()

        diff = fura.end_time - time

        return HttpResponse(diff.total_seconds())


def getSpots():
    spots = 55 - len(Driver.objects.all())
    if spots <= 0:
        return 'Na žalost so vsa mesta zasedena. Postavi se v čakalno vrsto in obvestili te bomo takoj, ko se kakšno mesto sprosti.'
    if spots == 1:
        return 'Pohiti, na voljo je samo še eno mesto!'
    if spots == 2:
        return 'Pohiti, na voljo sta samo še dve mesti!'
    if spots == 3:
        return 'Pohiti, na voljo so samo še 3 mesta!'
    if spots == 4:
        return 'Pohiti, na voljo so samo še 4 mesta!'
    if spots > 4:
        return 'Pohiti, na voljo je le še ' + str(spots) +' mest!'
    else:
        return ''

class UploadFileForm(forms.ModelForm):
    class Meta:
        model = postedImage
        fields = ['thetitle', 'theimage']

@csrf_exempt
def postImage(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed('Only POST here')

    form = UploadFileForm(request.POST, request.FILES)

    if not form.is_valid():
        return HttpResponseServerError('Invalid call')

    uploadedimage = form.save(commit=False)

    if request.FILES:
        uploadedimage.theimage = request.FILES

    uploadedimage.save()

    return HttpResponse('OK')


def maintenance(request, status_=None):
    context = {}
    try:
        context["replacing_battery"] = ReplacingBattery.objects.all()[0]
    except:
        context["replacing_battery"] = ReplacingBattery(status=False)
        context["replacing_battery"].save()
    if status_:
	print "change replaceing battery status", status_, bool(status_)
        context["replacing_battery"].status = bool(int(status_))
        context["replacing_battery"].save()

    return render_to_response('narodna/maintenance.html', context)


def iAmHere(request, driversecret):
    driver = Driver.objects.get(unique_string=driversecret)
    print driver.name, "is stil here"
    time = datetime.datetime.now() 
    fura = list(driver.fura_set.all())[-1]
    if fura.end_time < time:
        return JsonResponse({"status":"expire"})
    fura.last_seen = time
    fura.save()
    return JsonResponse({"status":"stil here"})


def updateWaitList(request):
    time = datetime.datetime.now()

    pavzaTime = datetime.timedelta(seconds=settings.PAVZA_TIME)
    furaTime = datetime.timedelta(seconds=settings.FURA_TIME)
    queryMinutes = 15

    expire_time = time-datetime.timedelta(seconds=8)
    nextFuras = Fura.objects.filter(end_time__gt=time, end_time__lt=time+datetime.timedelta(minutes=queryMinutes))
    while not nextFuras.filter(last_seen__gte=expire_time).order_by("end_time"):
        queryMinutes += 3
        nextFuras = Fura.objects.filter(end_time__gt=time, end_time__lt=time+datetime.timedelta(minutes=queryMinutes))
        if len(nextFuras) == len(Fura.objects.filter(end_time__gt=time)):
            if nextFuras.filter(last_seen__gte=expire_time).order_by("end_time"):
                break
            else:
                return JsonResponse({"status":"ni aktivnih fur"})

    expiredFuras = nextFuras.filter(last_seen__lt=expire_time).order_by("end_time")
    activeFuras = nextFuras.filter(last_seen__gte=expire_time).order_by("end_time")
    print "expired: ", len(expiredFuras), " active: ", len(activeFuras)

    if expiredFuras:
        #if first next fura is expired
        if expiredFuras[0].start_time < activeFuras[0].start_time:
            print "relist first"
            #if first expired fura is on drive
            expired_from = 0
            if expiredFuras[0].start_time < time:
                #"delete fura :)"
                expiredFuras[0].start_time = time - datetime.timedelta(seconds=2)
                expiredFuras[0].end_time = time - datetime.timedelta(seconds=1)
                expiredFuras[0].save()
                expired_from = 1
                cTime = datetime.datetime.now() + pavzaTime
            else:
                #if waiting for expired fura, make start time after pavza time to first ative fura
                cTime = datetime.datetime.now() + pavzaTime
                print "Aktivna prehiteva"

            for aFura in activeFuras:
                aFura.start_time = cTime
                aFura.end_time = cTime + furaTime
                aFura.save()
                cTime = cTime + pavzaTime + furaTime
            for eFura in expiredFuras[expired_from:]:
                eFura.start_time = cTime
                eFura.end_time = cTime + furaTime
                eFura.save()
                cTime = cTime + pavzaTime + furaTime
        else:
            print "running fura is ok"
            cTime = activeFuras[0].end_time + pavzaTime
            for aFura in activeFuras[1:]:
                aFura.start_time = cTime
                aFura.end_time = cTime + furaTime
                aFura.save()
                cTime = cTime + pavzaTime + furaTime
            for eFura in expiredFuras:
                eFura.start_time = cTime
                eFura.end_time = cTime + furaTime
                eFura.save()
                cTime = cTime + pavzaTime + furaTime
        return JsonResponse({"status":"wait list shuflled :)"})
    else:
        return JsonResponse({"status":"there is not expired furas"})


@require_http_methods(['POST'])
@csrf_protect
def signup_ajax(request):
    try:
        name = request.POST.get('name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
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
        return HttpResponse(secret)
    except:
        return HttpResponse(0)

@never_cache
def getPositionInWaitList(request, driversecret):
    try:
        driver = Driver.objects.get(unique_string=driversecret)
        fura = driver.fura_set.all()[0]
        time = datetime.datetime.now()
        nextFuras = Fura.objects.filter(end_time__gt=time).order_by("end_time")
        position = list(nextFuras).index(fura)
        time_to = fura.start_time-time
        if position == 0:
            time = time_to.seconds
        else:
            time = int(time_to.seconds/60)

        return JsonResponse({"position":position, "time_to":time})
    except:
        return JsonResponse({"position":-1, "time_to":-1})


def getImage(request):
    stream=urllib.urlopen('http://pelji.se/sub/testis')
    narodna = cStringIO.StringIO(urllib.urlopen("http://pelji.se/static/ng/img/stempl.png").read())
    bytes=''
    while True:
        bytes+=stream.read(1024)
        a = bytes.find('\xff\xd8')
        b = bytes.find('\xff\xd9')
        if a!=-1 and b!=-1:
            jpg = bytes[a:b+2]
            bytes= bytes[b+2:]
            break

    stream = io.BytesIO(jpg)
    img = Image.open(stream)
    over = Image.open(narodna)
    #over = over.resize((int(over.width/2), int(over.height/2)))
    img.paste(over, (img.width-over.width, img.height-over.height), over)


    file_name = "image_" + str(len(postedImage.objects.all())) + ".jpg"
    image_io = StringIO.StringIO()
    img.save(image_io, format='JPEG')
    image_file = InMemoryUploadedFile(image_io, None, file_name, 'image/jpeg', image_io.len, None)
    im = postedImage()
    im.theimage.save(file_name, image_file)
    im.thetitle = file_name
    im.save()

    return JsonResponse({"url": im.publicimageurl()})


def getWaitList(request):
    time = datetime.datetime.now()
    nextFuras = Fura.objects.filter(end_time__gt=time).order_by("end_time")
    return render_to_response('narodna/waitlist.html', {"waitlist":nextFuras})
