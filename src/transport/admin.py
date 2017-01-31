from django.contrib import admin
from transport.models import Line, LineStop, Stop, City

class LineStopInline(admin.TabularInline):
    model = LineStop
    readonly_fields = ('direction', 'stop')

class LineAdmin(admin.ModelAdmin):
    list_display = ('name', 'mode', 'full_name', 'providers')
    list_filter = ('mode', )
    search_fields = ('name', 'full_name', )
    inlines = (LineStopInline, )

class StopAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'providers')
    list_filter = ('city', )
    inlines = (LineStopInline, )

class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'insee_code')
    search_fields = ('name', 'insee_code')

admin.site.register(Line, LineAdmin)
admin.site.register(Stop, StopAdmin)
admin.site.register(City, CityAdmin)
