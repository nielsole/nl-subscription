from django.contrib import admin

# Register your models here.
from api.models import List, Subscriber

admin.site.register(List)
admin.site.register(Subscriber)