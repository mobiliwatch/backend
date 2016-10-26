from django.contrib import admin
from transport.models import Line, LineStop

class LineStopInline(admin.TabularInline):
    model = LineStop
    readonly_fields = ('direction', 'stop')

class LineAdmin(admin.ModelAdmin):
    list_display = ('name', 'mode', 'full_name', 'itinisere_id', 'metro_id')
    list_filter = ('mode', )
    search_fields = ('name', 'full_name', 'itinisere_id', 'metro_id')
    inlines = (LineStopInline, )

admin.site.register(Line, LineAdmin)
