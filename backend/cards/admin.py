from django.contrib import admin
from .models import Note
from .models import Column

admin.site.register(Note)
admin.site.register(Column)