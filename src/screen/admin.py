from django.contrib import admin
from screen.models import Screen

class ScreenAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'token', 'is_template' )
    list_filter = ('is_template', )

admin.site.register(Screen, ScreenAdmin)
