from django.contrib import admin
from narodna.models import Driver, Fura, EmailToSend, Options, postedImage

# Register your models here.
admin.site.register(Driver)
admin.site.register(Fura)
admin.site.register(EmailToSend)
admin.site.register(Options)
admin.site.register(postedImage)