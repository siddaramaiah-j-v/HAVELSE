from django.contrib import admin
from .models import Course,Playlists,Languages,Section
# Register your models here.

admin.site.register(Course)
admin.site.register(Section)
admin.site.register(Languages)
admin.site.register(Playlists)

