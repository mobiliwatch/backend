from django.contrib import admin
from region.models import City

class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'insee_code')
    search_fields = ('name', 'insee_code')

admin.site.register(City, CityAdmin)
