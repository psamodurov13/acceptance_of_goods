from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError

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

    def clean(self):
        cleaned_data = super().clean()
        employee_barcode = cleaned_data.get("employee_barcode")
        product_barcode = cleaned_data.get("product_barcode")
        all_employees_id = [i.barcode for i in Employees.objects.all()]
        all_products_id = [i.barcode for i in Products.objects.all()]

        errors = {}
        if employee_barcode not in all_employees_id:
            logger.info('Raise VE1')
            errors['employee_barcode'] = ValidationError("Сотрудник с таким штрихкодом не существует")
        if product_barcode not in all_products_id:
            logger.info('Raise VE2')
            errors['product_barcode'] = ValidationError("Товар с таким штрихкодом не существует")
        if errors:
            raise ValidationError(errors)



class AcceptanceFilterForm(forms.Form):
    # employee = forms.MultipleChoiceField(label='Испольнитель', choices=((i.pk, i.name) for i in Employees.objects.all()),
    #                              required=False, widget=forms.CheckboxSelectMultiple(),
    #                                      initial=[c.pk for c in Employees.objects.all()])
    start_date = forms.DateField(label='От', input_formats=['%d.%m.%Y'], widget=forms.DateInput(attrs={'class': 'datetimepicker'}))
    end_date = forms.DateField(label='До', input_formats=['%d.%m.%Y'], widget=forms.DateInput(attrs={'class': 'datetimepicker'}))


class ReportFilterForm(forms.Form):
    choices = []
    for category in ProductCategories.objects.all().order_by('id'):
        choices.append((f'category_{category.pk}', category.name))
        logger.info(f'CATEGORY - {category.name}')
        for product in Products.objects.filter(category=category).order_by('name'):
            choices.append((product.pk, product.name))
            logger.info(f'---PRODUCT - {product.name}')
    logger.info(f'CHOICES - {choices}')

    # employee = forms.MultipleChoiceField(label='Испольнитель', choices=((i.pk, i.name) for i in Employees.objects.all()),
    #                              required=False, widget=forms.CheckboxSelectMultiple(),
    #                                      initial=[c.pk for c in Employees.objects.all()])
    start_date = forms.DateField(label='От', input_formats=['%d.%m.%Y'], widget=forms.DateInput(attrs={'class': 'datetimepicker'}))
    end_date = forms.DateField(label='До', input_formats=['%d.%m.%Y'], widget=forms.DateInput(attrs={'class': 'datetimepicker'}))
    products = forms.MultipleChoiceField(label='Товары', choices=choices,
                                 required=False, widget=forms.CheckboxSelectMultiple(attrs={'class': 'custom'}),
                                         initial=[c[0] for c in choices])

    def __init__(self, *args, **kwargs):
        try:
            employees = kwargs.get('initial')['employees']
        except TypeError:
            logger.info(f'NOT INITIAL IN KWARGS')
            employees = Employees.objects.all()
        super().__init__(*args, **kwargs)
        logger.info(f'EMPLOYEES FROM FORM {employees}')
        self.fields['employee'] = forms.MultipleChoiceField(label='Испольнитель',
                                             choices=((i.pk, i.name) for i in Employees.objects.all()),
                                             required=False, widget=forms.CheckboxSelectMultiple(),
                                             initial=[c.pk for c in employees])


class ChangeScheduleForm(forms.Form):
    choices = [('Р', 'Р'), ('В', 'В'), ('Б', 'Б'), ('О', 'О')]
    logger.info(f'CHOICES - {choices}')

    date = forms.DateField(label='Дата', input_formats=['%d.%m.%Y'], widget=forms.DateInput(attrs={'class': 'datetimepicker'}))
    type_of_day = forms.ChoiceField(label='День', choices=choices,
                                 required=True, widget=forms.Select(attrs={'class': 'custom'}),
                                         initial=[c[0] for c in choices])


