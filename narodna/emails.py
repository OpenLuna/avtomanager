# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from narodna.models import EmailToSend, Driver
import datetime
import time
from pytz import timezone

pozdravnimail = {
    'subject': u'Jutri vožiš robota v Narodni galeriji!',
    'content': u'Zdravo {{ IME }}, \n\nhvala za prijavo! \n\nRobot bo zate pripravljen jutri ob {{ URA }}. Do robota dostopaš na tem skrivnem linku: http://pelji.se/{{ SECRET }}. Ure se moraš natančno držati, saj so čisto vsi termini zasedeni.\n\nČe se ti zdi, da zaradi kakršnega koli razloga ne zmoreš ob tej uri, odgovori na ta mail. Se bomo potrudili, da zažongliramo razpored, ali pa vožnjo omogočimo komu, ki je ostal brez. :)\n\nUživaj! \n\nNarodna galerija',
    'html': u'<!DOCTYPE html><html><head></head><body><h2>Zdravo, {{ IME }},</h2><p>hvala za prijavo!</p><p>Robot bo zate pripravljen jutri ob {{ URA }}. Do robota dostopaš na tem skrivnem linku: http://pelji.se/{{ SECRET }}. Ure se moraš natančno držati, saj so čisto vsi termini zasedeni.</p><p>Se vidimo!</p><p>Če se ti zdi, da zaradi kakršnega koli razloga ne zmoreš ob tej uri, odgovori na ta mail. Se bomo potrudili, da zažongliramo razpored, ali pa vožnjo omogočimo komu, ki je ostal brez. :)</p><p>Uživaj!</p></body></html>',
    'sender': 'Narodna galerija <robot@pelji.se>'
}

polureprejemail = {
    'subject': u'Čez pol ure voziš robota v Narodni galeriji!',
    'html': u'<!DOCTYPE html><html><head></head><h2>Zdravo {{ IME }},<h2><p>danes je tvoj dan! Robot čaka nate. Na vrsti si točno ob {{ URA }}. <a href="http://pelji.se/{{ SECRET }}">Pridi na prizorišče</a> kako minuto prej, da prebereš navodila in se ogreješ.</p><p>Uživaj!</p><p>Narodna galerija</p></body></html>',
    'content': u'Zdravo, {{ IME }}, danes je tvoj dan! Robot čaka nate. Na vrsti si točno ob {{ URA }}. Pridi na prizorišče (http://pelji.se/{{ SECRET }}) kako minuto prej, da prebereš navodila in se ogreješ.\n\nUživaj!\n\nNarodna galerija',
    'sender': 'Narodna galerija <robot@pelji.se>'
}

def parseContent(content, keyvalues):
    finaltext = content

    for key in keyvalues:
#        print key, keyvalues[key]
        finaltext = finaltext.replace(u'{{ ' + key.upper() + ' }}', keyvalues[key])

    return finaltext

def sendPozdravniMail(istest=True):
    if not istest:

        d = Driver.objects.all()

        drivers = [driver for driver in d if len(driver.fura_set.all()) > 0]

        for driver in drivers:
            print driver.email
            driversecret = driver.unique_string

            recipient = driver.email

            subject = pozdravnimail['subject']

            text_content = parseContent(
                pozdravnimail['content'],
                {
                    'ime': driver.name,
                    'ura': datetime.datetime.strftime(driver.fura_set.all()[0].start_time, '%H:%M'),
                    'secret': driversecret
                }
            )

            from_email = pozdravnimail['sender']

            html_content = parseContent(
                pozdravnimail['html'],
                {
                    'ime': driver.name,
                    'ura': datetime.datetime.strftime(driver.fura_set.all()[0].start_time, '%H:%M'),
                    'secret': driversecret
                }
            )


            # Send it:
            send_mail(subject, text_content, from_email, [recipient], html_message=html_content)
            print 'Email sent'
            print 'Sleeping'
            time.sleep(10)
            print 'Woke up'

    else:
        driver = Driver.objects.get(email='lana.lucin@gmail.com')

        driversecret = driver.unique_string

        recipient = driver.email

        subject = pozdravnimail['subject']

        text_content = parseContent(
            pozdravnimail['content'],
            {
                'ime': driver.name,
                'ura': datetime.datetime.strftime(driver.fura_set.all()[0].start_time, '%H:%M'),
                'secret': driversecret
            }
        )

        from_email = pozdravnimail['sender']

        html_content = parseContent(
            pozdravnimail['html'],
            {
                'ime': driver.name,
                'ura': datetime.datetime.strftime(driver.fura_set.all()[0].start_time, '%H:%M'),
                'secret': driversecret
            }
        )


        # Send it:
        send_mail(subject, text_content, from_email, [recipient], html_message=html_content)
        print 'Email sent'

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
        ), 'text/html')


        # Send it:
        msg.send()
        print 'Email sent'

        email.sent = True
        email.save()
        print 'Email object updated'
