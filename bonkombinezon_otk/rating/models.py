from django.db import models
from bonkombinezon_otk.utils import CustomStr


class RatingRange(CustomStr, models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    min_value = models.FloatField(verbose_name='Минимальное значение')
    max_value = models.FloatField(verbose_name='Максимальное значение')
    color = models.CharField(verbose_name='Код цвета фона', help_text='Код цвета фона в HEX формате')
    text_color = models.CharField(verbose_name='Код цвета текста', help_text="Код цвета текста в HEX формате",
                                  default="000000")

    class Meta:
        verbose_name = 'Интервал рейтинга'
        verbose_name_plural = 'Интервалы рейтинга'


class TimePeriod(CustomStr, models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    period = models.IntegerField(verbose_name='Временной период',
                                 help_text='Введите количество недель для расчета рейтинга')

    class Meta:
        verbose_name = 'Временной период'
        verbose_name_plural = 'Временной период'
