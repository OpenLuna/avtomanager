import datetime
from signups.models import Fura
from django.conf import settings
from pytz import timezone

def getTimes():
    
    time = datetime.datetime.now()
#    tz = timezone(settings.TIME_ZONE)
#    time = time.replace(tzinfo = tz)
    
    zadnjafura = Fura.objects.all().order_by('end_time').reverse()
    
    if len(zadnjafura) > 0:
        if time < zadnjafura[0].end_time:
            time = zadnjafura[0].end_time
        else:
            time = time + datetime.timedelta(minutes=10)
    else:
        return 0
    
    # can fit in current day
    if not ((time.time().hour == 21 and time.time().minute > 57) or time.time().hour > 21):
    
        datumfure = time.date()
        
        start = time + datetime.timedelta(seconds=settings.PAVZA_TIME)
        end = start + datetime.timedelta(seconds=settings.FURA_TIME)
    
    # can not fit in current day
    else:
    
        datumfure = time + datetime.timedelta(days=1)
        
        start = datetime.datetime.combine(datumfure, datetime.datetime.strptime('12', '%H').time())
        end = start + datetime.timedelta(seconds=settings.FURA_TIME)
    
    return {'start': start, 'end': end, 'date': datumfure}
