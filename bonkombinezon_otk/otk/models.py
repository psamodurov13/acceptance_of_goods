from datetime import datetime

from django.db import models
from django.urls import reverse
from bonkombinezon_otk.utils import CustomStr, default_schedule
from datetime import date


class Employees(CustomStr, models.Model):
    name = models.CharField(max_length=255, verbose_name='Фамилия Имя Отчество')
    barcode = models.CharField(max_length=128, verbose_name='Штрихкод')
    schedule = models.JSONField(verbose_name='График работы', blank=True, null=True)
    status = models.BooleanField(verbose_name='Статус', default=True)

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
        ordering = ['name']


class ProductCategories(CustomStr, models.Model):
    name = models.CharField(max_length=255, verbose_name='Название группы товаров')
    amount = models.IntegerField(verbose_name='Плата за изделие', blank=True, null=True)

    def get_absolute_url(self):
        return reverse('categories', kwargs={'pk': self.pk})

    class Meta:
        verbose_name = 'Группа товара'
        verbose_name_plural = 'Группы товаров'


class Products(CustomStr, models.Model):
    name = models.CharField(max_length=255, verbose_name='Название изделия')
    barcode = models.CharField(max_length=128, verbose_name='Штрихкод изделия', unique=True)
    category = models.ForeignKey(ProductCategories, on_delete=models.CASCADE, related_name='products',
                                 verbose_name='Группа товаров')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


def default_datetime(): return datetime.now()


class Acceptance(CustomStr, models.Model):
    employee = models.ForeignKey(Employees, on_delete=models.CASCADE, related_name='acceptances',
                                 verbose_name='Сотрудник')
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='acceptances',
                                verbose_name='Товар')
    acceptance_date = models.DateTimeField(verbose_name='Дата приемки', default=default_datetime)


    class Meta:
        verbose_name = 'Приемка'
        verbose_name_plural = 'Приемки'