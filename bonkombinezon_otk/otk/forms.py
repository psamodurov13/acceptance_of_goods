from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from .models import *
from bonkombinezon_otk.settings import logger


class UserRegisterForm(UserCreationForm):
    username = forms.CharField(label="Имя пользователя", widget=forms.TextInput())
    email = forms.EmailField(label="e-mail", widget=forms.EmailInput())
    password1 = forms.CharField(label="Введите пароль", widget=forms.PasswordInput())
    password2 = forms.CharField(label="Повторите пароль", widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label='Имя пользователя', widget=forms.TextInput())
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput())


class LoadProductsForm(forms.Form):
    file = forms.FileField(label="Выберите файл", widget=forms.FileInput())


class CreateAcceptanceForm(forms.Form):
    employee_barcode = forms.CharField(label="Отсканировать штрихкод сотрудника", widget=forms.TextInput())
    product_barcode = forms.CharField(label="Отсканировать штрихкод изделия", widget=forms.TextInput())


class AcceptanceFilterForm(forms.Form):
    employee = forms.MultipleChoiceField(label='Испольнитель', choices=((i.pk, i.name) for i in Employees.objects.all()),
                                 required=False, widget=forms.CheckboxSelectMultiple(),
                                         initial=[c.pk for c in Employees.objects.all()])
    start_date = forms.DateField(label='От')
    end_date = forms.DateField(label='До')


class ReportFilterForm(forms.Form):
    choices = []
    for category in ProductCategories.objects.all().order_by('id'):
        choices.append((f'category_{category.pk}', category.name))
        logger.info(f'CATEGORY - {category.name}')
        for product in Products.objects.filter(category=category).order_by('name'):
            choices.append((product.pk, product.name))
            logger.info(f'---PRODUCT - {product.name}')
    logger.info(f'CHOICES - {choices}')

    employee = forms.MultipleChoiceField(label='Испольнитель', choices=((i.pk, i.name) for i in Employees.objects.all()),
                                 required=False, widget=forms.CheckboxSelectMultiple(),
                                         initial=[c.pk for c in Employees.objects.all()])
    start_date = forms.DateField(label='От')
    end_date = forms.DateField(label='До')
    products = forms.MultipleChoiceField(label='Товары', choices=choices,
                                 required=False, widget=forms.CheckboxSelectMultiple(attrs={'class': 'custom'}),
                                         initial=[c[0] for c in choices])
