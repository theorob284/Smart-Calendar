from django.contrib import admin
from .models import Event, ConflictRecord

# Enable Event and ConflictRecord management via Django admin

admin.site.register(Event)
admin.site.register(ConflictRecord)
