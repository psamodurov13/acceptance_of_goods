# Generated by Django 4.2.2 on 2023-06-15 19:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('otk', '0002_alter_employees_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='acceptance',
            options={'verbose_name': 'Приемка', 'verbose_name_plural': 'Приемки'},
        ),
        migrations.AlterModelOptions(
            name='productcategories',
            options={'verbose_name': 'Группа товара', 'verbose_name_plural': 'Группы товаров'},
        ),
        migrations.AlterModelOptions(
            name='products',
            options={'verbose_name': 'Товар', 'verbose_name_plural': 'Товары'},
        ),
    ]
