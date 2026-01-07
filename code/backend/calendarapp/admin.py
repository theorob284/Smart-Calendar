from django.contrib import admin
from .models import Event, ConflictRecord, AlternativeGroup

# Register your models here.

admin.site.register(Event)
admin.site.register(ConflictRecord)
admin.site.register(AlternativeGroup)