# Generated by Django 4.2.2 on 2023-07-17 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rating', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ratingrange',
            name='name',
            field=models.CharField(default=1, max_length=100, verbose_name='Название'),
            preserve_default=False,
        ),
    ]