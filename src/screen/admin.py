from django.contrib import admin
from screen.models import Screen

class ScreenAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'token', )

admin.site.register(Screen, ScreenAdmin)
