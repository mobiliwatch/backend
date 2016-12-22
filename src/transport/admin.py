from django.contrib import admin
from transport.models import Line, LineStop, Stop, City

class LineStopInline(admin.TabularInline):
    model = LineStop
    readonly_fields = ('direction', 'stop')

class LineAdmin(admin.ModelAdmin):
    list_display = ('name', 'mode', 'full_name', 'itinisere_id', 'metro_id')
    list_filter = ('mode', )
    search_fields = ('name', 'full_name', 'itinisere_id', 'metro_id')
    inlines = (LineStopInline, )

class StopAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'itinisere_id', 'metro_id', 'metro_cluster')
    list_filter = ('city', )
    inlines = (LineStopInline, )

class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'insee_code')
    search_fields = ('name', 'insee_code')

admin.site.register(Line, LineAdmin)
admin.site.register(Stop, StopAdmin)
admin.site.register(City, CityAdmin)
