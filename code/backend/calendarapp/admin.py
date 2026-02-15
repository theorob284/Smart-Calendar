from django.contrib import admin
from .models import Event, ConflictRecord

# Register your models here.

admin.site.register(Event)
admin.site.register(ConflictRecord)
