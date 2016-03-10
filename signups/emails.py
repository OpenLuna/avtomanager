# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from signups.models import EmailToSend
import datetime
from pytz import timezone

pozdravnimail = {
    'subject': u'Shrani ta mail!',
    'content': u'Zdravo, {{ IME }}, \n\nhvala za prijavo! \n\nSteza bo zate pripravljena {{ DATUM }} ob {{ URA }}. Do nje lahko dostopaš samo tukaj: http://pelji.se/{{ SECRET }}. \n\nSe vidimo! \n\nZavarovalnica Tilia',
    'html': u'<h2>Zdravo, {{ IME }},</h2><p>hvala za prijavo!</p><p>Steza bo zate pripravljena {{ DATUM }} ob {{ URA }}. Do nje lahko dostopaš samo tukaj: http://pelji.se/{{ SECRET }}.</p><p>Se vidimo!</p><p>Zavarovalnica Tilia</p>',
    'sender': 'Zavarovalnica Tilia <avto@pelji.se>'
}

polureprejemail = {
    'subject': u'Se vidimo kmalu!',
    'content': u'<h2>Zdravo, {{ IME }},<h2><p>danes je tvoj dan! Za spretnostno vožnjo na daljavo si na vrsti točno ob {{ URA }}. <a href="http://pelji.se/{{ SECRET }}">Pridi na prizorišče</a> kako minuto prej, da prebereš navodila in se ogreješ.</p><p>Srečno!</p><p>Zavarovalnica Tilia</p>',
    'content': u'Zdravo, {{ IME }}, danes je tvoj dan! Za spretnostno vožnjo na daljavo si na vrsti točno ob {{ URA }}. Pridi na prizorišče (http://pelji.se/{{ SECRET }}) kako minuto prej, da prebereš navodila in se ogreješ. Srečno! Zavarovalnica Tilia',
    'sender': 'Zavarovalnica Tilia <avto@pelji.se>'
}

def parseContent(content, keyvalues):
    finaltext = content
    
    for key in keyvalues:
#        print key, keyvalues[key]
        finaltext = finaltext.replace(u'{{ ' + key.upper() + ' }}', keyvalues[key])
    
    return finaltext

def sendReminder():
    emails = EmailToSend.objects.filter(sent=False).order_by('time')
    
    if len(emails) < 1:
        return
    
    email = emails[0]
    
    time = datetime.datetime.now()
#    tz = timezone(settings.TIME_ZONE)
#    time = time.replace(tzinfo = tz)
    
    if (email.time - datetime.timedelta(seconds=30)) <= time: # <= (email.time + timedelta(seconds=30)):
        
        name = email.driver.name
        start_time = email.driver.fura_set.all()[0].start_time
        driverid = email.driver.id
        driversecret = email.driver.unique_string
        
        # send reminder email
        msg = EmailMultiAlternatives(
            subject = polureprejemail['subject'],
            body = parseContent(
                polureprejemail['content'],
                {
                    'ime': name,
                    'ura': datetime.datetime.strftime(email.driver.fura_set.all()[0].start_time, '%H:%M'),
                    'secret': driversecret
                }
            ),
            from_email = polureprejemail['sender'],
            to = [email.driver.email],
            headers={
                'Reply-To': polureprejemail['sender']
            } # optional extra headers
        )
    
        msg.attach_alternative(parseContent(
            polureprejemail['content'],
            {
                'ime': name,
                'ura': datetime.datetime.strftime(email.driver.fura_set.all()[0].start_time, '%H:%M'),
                'secret': driversecret
            }
        ),"text/html")


        # Send it:
        msg.send()
        print 'Email sent'
        
        email.sent = True
        email.save()
        print 'Email object updated'