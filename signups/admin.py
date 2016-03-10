from django.contrib import admin
from signups.models import Driver, Fura, EmailToSend, Options

# Register your models here.
admin.site.register(Driver)
admin.site.register(Fura)
admin.site.register(EmailToSend)
admin.site.register(Options)