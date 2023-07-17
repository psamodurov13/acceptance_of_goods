from django.contrib import admin
from .models import *


class RatingRangeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'min_value', 'max_value')
    list_display_links = ('id', 'name')
    save_as = True
    save_on_top = True


admin.site.register(RatingRange, RatingRangeAdmin)
