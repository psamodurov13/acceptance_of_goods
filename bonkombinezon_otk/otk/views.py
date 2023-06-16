from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView
from .forms import UserRegisterForm, UserLoginForm, LoadProductsForm
from django.contrib.auth import login, logout
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from loguru import logger
from django.views.generic.edit import CreateView, UpdateView, DeleteView
import openpyxl
from bonkombinezon_otk.utils import *



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
    return render(request, 'otk/add_acceptance.html', context)


def products_catalog(request):
    products = Products.objects.all()
    categories = ProductCategories.objects.all()
    context = {
        'title': 'Редактирование номенклатуры',
        'products': products,
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