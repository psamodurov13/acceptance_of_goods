from django.contrib import admin
from .models import *
# from bonkombinezon_otk.utils import CustomStr


class RatingRangeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'min_value', 'max_value')
    list_display_links = ('id', 'name')
    save_as = True
    save_on_top = True


class TimePeriodAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'period')
    list_display_links = ('id', 'name', 'period')
    save_as = True
    save_on_top = True


admin.site.register(RatingRange, RatingRangeAdmin)
admin.site.register(TimePeriod, TimePeriodAdmin)
