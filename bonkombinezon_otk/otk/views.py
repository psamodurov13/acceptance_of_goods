from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView
from .forms import UserRegisterForm, UserLoginForm, LoadProductsForm, CreateAcceptanceForm, AcceptanceFilterForm
from django.contrib.auth import login, logout
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from loguru import logger
from django.views.generic.edit import CreateView, UpdateView, DeleteView
import openpyxl
from bonkombinezon_otk.utils import *
from datetime import datetime, timedelta


@login_required
def index(request):
    context = {
        'title': 'Home page'
    }
    return render(request, 'otk/index.html', context)


def login_page(request):
    login_form = UserLoginForm()
    register_form = UserRegisterForm()
    context = {
        'login_form': login_form,
        'register_form': register_form
    }
    return render(request, 'otk/login.html', context)


def user_login(request):
    if request.method == 'POST' and 'login-button' in request.POST:
        login_form = UserLoginForm(data=request.POST)
        # register_form = UserRegisterForm()
        if login_form.is_valid():
            user = login_form.get_user()
            login(request, user)
            messages.success(request, 'Вход выполнен')
        else:
            register_form = UserRegisterForm()
            messages.error(request, 'Вход не выполнен, проверьте форму')
            return render(request, 'otk/login.html', {'login_form': login_form, 'register_form': register_form})
    # else:
    #     login_form = UserLoginForm()
    #     register_form = UserRegisterForm()
    return redirect('home')


def user_register(request):
    if request.method == 'POST' and 'register-button' in request.POST:
        register_form = UserRegisterForm(data=request.POST)
        if register_form.is_valid():
            user = register_form.save()
            login(request, user)
            messages.success(request, 'Вы успешно зарегистрировались. После модерации Вы получите доступ к функционалу')
        else:
            login_form = UserLoginForm()
            messages.error(request, 'Вы не зарегистрировались. Проверьте форму')
            return render(request, 'otk/login.html', {'login_form': login_form, 'register_form': register_form})
    return redirect('home')


def user_logout(request):
    logout(request)
    messages.success(request, 'Вы вышли из аккаунта')
    return redirect('home')


def admin_page(request):
    context = {
        'title': 'Страница администратора'
    }
    return render(request, 'otk/admin_page.html', context)


def add_acceptance(request):
    context = {
        'title': 'Приемка изделия'
    }
    if request.method == 'POST':
        form = CreateAcceptanceForm(request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            logger.info(f'ADD ACCEPTANCE FORM DATA - {form_data}')
            employee = Employees.objects.get(barcode=form_data['employee_barcode'])
            logger.info(f'EMPLOYEE FOR ACCEPTANCE - {employee}')
            product = Products.objects.get(barcode=form_data['product_barcode'])
            logger.info(f'PRODUCT FOR ACCEPTANCE - {product}')
            new_acceptance = Acceptance.objects.create(
                employee=employee,
                product=product
            )
            logger.info(f'NEW ACCEPTANCE WAS CREATED - {new_acceptance}')
            messages.success(request, f'Создана новая приемка изделия')
        else:
            messages.error(request, 'Допущена ошибка. Проверьте форму')
            return render(request, 'otk/add_acceptance.html', context)
    form = CreateAcceptanceForm()
    context['form'] = form
    return render(request, 'otk/add_acceptance.html', context)


def acceptance_list(request):
    context = {
        'title': 'Редактировать данные внесенные ранее'
    }
    if request.method == 'POST':
        form = AcceptanceFilterForm(request.POST)
        logger.info(f'REQUEST POST DATA - {request.POST}')
        if form.is_valid():
            form_data = form.cleaned_data
            logger.info(f'ACCEPTANCE LIST FORM DATA - {form_data}')
            employees = Employees.objects.filter(id__in=form_data['employee'])
            logger.info(f'EMPLOYEES - {employees}')
            start_date = form_data['start_date']
            end_date = form_data['end_date']
            acceptances = Acceptance.objects.filter(acceptance_date__range=[start_date, end_date],
                                                    employee__in=employees)
            logger.info(f'FILTRED ACCEPTANCES {start_date} - {end_date} / {acceptances}')
        else:
            form_data = form.cleaned_data
            logger.info(f'INVALID FORM')
            logger.info(f'ACCEPTANCE LIST FORM DATA - {form_data}')
            logger.info(f'ERRORS - {form.errors}')
            acceptances = None
    else:
        form = AcceptanceFilterForm()
        end_date = datetime.today()
        start_date = end_date - timedelta(days=14)
        acceptances = Acceptance.objects.filter(acceptance_date__range=[start_date, end_date])
        logger.info(f'ALL ACCEPTANCES FOR DATERANGE {start_date} - {end_date} / {acceptances}')
    context['form'] = form
    context['acceptances'] = acceptances
    return render(request, 'otk/acceptance_list.html', context)


# class CreateAcceptance(CustomStr, CreateView):
#     model = Acceptance
#     fields = ['name', 'barcode', 'category']
#     success_url = reverse_lazy('products_catalog')
#
#     def form_valid(self, form):
#         """If the form is valid, save the associated model."""
#         self.object = form.save()
#         messages.success(self.request, 'Товар добавлен')
#         return super().form_valid(form)


def products_catalog(request):
    products = Products.objects.all().order_by('id')
    paginator = Paginator(products, 25)  # сколько записей на 1 странице
    page_number = request.GET.get('page')  # GET параметр page
    page_obj = paginator.get_page(page_number)
    categories = ProductCategories.objects.all()
    context = {
        'title': 'Редактирование номенклатуры',
        'page_obj': page_obj,
        'categories': categories
    }
    return render(request, 'otk/products_catalog.html', context)


class CreateCategory(CustomStr, CreateView):
    model = ProductCategories
    fields = ['name', 'amount']
    success_url = reverse_lazy('products_catalog')

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save()
        messages.success(self.request, 'Группа товаров добавлена')
        return super().form_valid(form)


class EditCategory(CustomStr, UpdateView):
    model = ProductCategories
    fields = ['name', 'amount']
    success_url = reverse_lazy('products_catalog')
    template_name_suffix = '_edit_form'

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save()
        messages.success(self.request, 'Группа товаров изменена')
        return super().form_valid(form)


class DeleteCategory(CustomStr, DeleteView):
    model = ProductCategories
    success_url = reverse_lazy('products_catalog')

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(self.request, 'Группа товаров удалена')
        return HttpResponseRedirect(success_url)


class CreateProduct(CustomStr, CreateView):
    model = Products
    fields = ['name', 'barcode', 'category']
    success_url = reverse_lazy('products_catalog')

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save()
        messages.success(self.request, 'Товар добавлен')
        return super().form_valid(form)


class EditProduct(CustomStr, UpdateView):
    model = Products
    fields = ['name', 'barcode', 'category']
    success_url = reverse_lazy('products_catalog')
    template_name_suffix = '_edit_form'

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save()
        messages.success(self.request, 'Товар изменен')
        return super().form_valid(form)


class DeleteProduct(CustomStr, DeleteView):
    model = Products
    success_url = reverse_lazy('products_catalog')

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(self.request, 'Товар удален')
        return HttpResponseRedirect(success_url)


def load_products(request):
    context = {
        'title': 'Загрузка товаров из XLSX',
    }
    if request.method == 'POST':
        form = LoadProductsForm(request.POST, request.FILES)
        context['form'] = form
        if form.is_valid():
            form_data = form.cleaned_data
            logger.info(f'FILES - {form_data["file"]}')
            workbook = openpyxl.load_workbook(form_data["file"])
            sheets = workbook.sheetnames
            worksheet = workbook[sheets[0]]
            products = []
            for i in tuple(worksheet.rows):
                category = str(i[0].value)
                name = f'{i[2].value} {i[4].value} {i[5].value}'
                barcode = str(i[3].value)
                products.append({'name': name, 'barcode': barcode, 'category': category})
            logger.info(f'TOTAL PRODUCTS - {len(products)}, EXAMPLE - {products[0]}')
            new_products = []
            new_categories = []
            for product in products:
                current_product = safe_get(Products, name=product['name'], barcode=product['barcode'])
                if current_product:
                    logger.info(f'PRODUCT ALREADY EXIST {current_product}')
                else:
                    current_category = safe_get(ProductCategories, name=product['category'])
                    if current_category:
                        logger.info(f'CATEGORY ALREADY EXIST {current_category}')
                    else:
                        current_category = ProductCategories.objects.create(
                            name=product['category']
                        )
                        new_categories.append(current_category)
                        logger.info(f'NEW CATEGORY {current_category} WAS CREATED')
                    new_product = Products.objects.create(
                        name=product['name'],
                        barcode=product['barcode'],
                        category=current_category
                    )
                    new_products.append(new_product)
                    logger.info(f'NEW PRODUCT {new_product} WAS CREATED')
            logger.info(f'Файл загружен. Загружено товаров {len(new_products)}/{len(products)}. '
                        f'Создано новых категорий - {len(new_categories)}')
            messages.success(request, f'Файл загружен. Загружено товаров {len(new_products)}/{len(products)}\n'
                                      f'Создано новых категорий - {len(new_categories)}. Не забудьте проставить им цены')
            return redirect('products_catalog')
        else:
            messages.error(request, 'Файл не загружен')
            return render(request, 'otk/load_products.html', context)
    else:
        form = LoadProductsForm()
        context['form'] = form
    return render(request, 'otk/load_products.html', context)


def employees_catalog(request):
    employees = Employees.objects.all().order_by('id')
    paginator = Paginator(employees, 25)  # сколько записей на 1 странице
    page_number = request.GET.get('page')  # GET параметр page
    page_obj = paginator.get_page(page_number)
    context = {
        'title': 'Текущие сотрудники',
        'page_obj': page_obj,
    }
    return render(request, 'otk/employees_catalog.html', context)


class CreateEmployee(CustomStr, CreateView):
    model = Employees
    fields = ['name', 'barcode']
    success_url = reverse_lazy('employees_catalog')

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save()
        messages.success(self.request, 'Сотрудник добавлен')
        return super().form_valid(form)


class EditEmployee(CustomStr, UpdateView):
    model = Employees
    fields = ['name', 'barcode']
    success_url = reverse_lazy('employees_catalog')
    template_name_suffix = '_edit_form'

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save()
        messages.success(self.request, 'Сотрудник изменен')
        return super().form_valid(form)


class DeleteEmployee(CustomStr, DeleteView):
    model = Employees
    success_url = reverse_lazy('employees_catalog')

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(self.request, 'Сотрудник удален')
        return HttpResponseRedirect(success_url)


class EditAcceptance(CustomStr, UpdateView):
    model = Acceptance
    fields = ['employee', 'product', 'acceptance_date']
    success_url = reverse_lazy('acceptance_list')
    template_name_suffix = '_edit_form'

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save()
        messages.success(self.request, 'Приемка изменена')
        return super().form_valid(form)


class DeleteAcceptance(CustomStr, DeleteView):
    model = Acceptance
    success_url = reverse_lazy('acceptance_list')

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.delete()
        messages.success(self.request, 'Приемка удалена')
        return HttpResponseRedirect(success_url)