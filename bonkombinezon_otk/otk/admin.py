from django.contrib import admin
from .models import *


class EmployeesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'barcode')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'barcode')
    save_as = True
    save_on_top = True


class ProductCategoriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'amount')
    list_display_links = ('id', 'name')
    search_fields = ('name',)
    save_as = True
    save_on_top = True


class ProductsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'barcode', 'category')
    list_display_links = ('id', 'name')
    search_fields = ('name', 'barcode')
    list_filter = ('category',)
    save_as = True
    save_on_top = True


class AcceptanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'product', 'acceptance_date')
    list_display_links = ('id', )
    search_fields = ('employee', 'product')
    list_filter = ('employee', 'product')
    save_as = True
    save_on_top = True


admin.site.register(Employees, EmployeesAdmin)
admin.site.register(ProductCategories, ProductCategoriesAdmin)
admin.site.register(Products, ProductsAdmin)
admin.site.register(Acceptance, AcceptanceAdmin)