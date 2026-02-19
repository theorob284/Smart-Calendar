from django.contrib import admin
from .models import *

# Enable Event and ConflictRecord management via Django admin

admin.site.register(Document)
admin.site.register(ExtractedEventCandidate)