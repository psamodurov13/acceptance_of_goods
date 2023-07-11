import time
import pandas as pd
from bonkombinezon_otk.settings import BASE_DIR
from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView
from .forms import *
from django.contrib.auth import login, logout
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from loguru import logger
from django.views.generic.edit import CreateView, UpdateView, DeleteView
import openpyxl
from bonkombinezon_otk.utils import *
from datetime import datetime, timedelta
from excel_response import ExcelResponse
import pytz
our_timezone = pytz.timezone('Asia/Omsk')


def get_results(start_date=datetime.today() - timedelta(days=14), end_date=datetime.today(),
                employees=Employees.objects.all(),
                all_products=None):
    logger.info(f'FUNCTION GET_RESULTS IS STARTED')
    categories = ProductCategories.objects.all()
    head_row = ['Сотрудник'] + [i.name for i in categories] + ['Сумма за период']
    final_row = ['Итого'] + [0] * len(categories) + [0]
    logger.info(f'FINAL ROW {final_row}')
    logger.info(f'HEAD ROW ')
    end_date = datetime(end_date.year, end_date.month, end_date.day)
    logger.info(f'start_date {start_date}')
    logger.info(f'end_date - {datetime(end_date.year, end_date.month, end_date.day, tzinfo=our_timezone)}')
    end_date = end_date + timedelta(1)
    if not all_products:
        all_products = Products.objects.all()
    results = []
    acceptances = None
    for employee in employees:
        logger.info('-' * 10)
        logger.info(f'START FORM DATA FOR {employee.name}')
        result = [employee.name]
        total = 0
        for category in categories:
            products = all_products.filter(
                category=category
            )
            logger.info(f'ALL PRODUCTS OF CATEGORY {category} - {products}')
            acceptances = Acceptance.objects.filter(
                product__in=products,
                employee=employee,
                acceptance_date__range=[start_date, end_date]
            )
            logger.info(f'ALL ACCEPTANCES OF CATEGORY {category} - {acceptances}')
            counts = acceptances.count()
            result.append(counts)
            logger.info(f'RESULT - {result}')
            if not category.amount:
                return False
            total += counts * category.amount
            logger.info(f'CURRENT TOTAL - {counts * category.amount}')
        result.append(total)
        results.append(result)
        for index, value in enumerate(result[1:], start=1):
            logger.info(f'value - {value}')
            logger.info(f'final_row[index] - {final_row[index]}')
            final_row[index] += value
        logger.info(f'CURRENT FINAL ROW - {final_row}')

    logger.info(f'RESULTS - {results}')
    logger.info(f'ALL ACCEPTANCES FOR DATERANGE {start_date} - {end_date} / {acceptances}')
    return head_row, results, final_row


@login_required
def index(request):
    context = {
        'title': 'Home page'
    }
    categories = ProductCategories.objects.all()
    head_row = ['Время', 'Сотрудник'] + [i.name for i in categories]
    results = []
    today = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
    logger.info(f'TODAY - {datetime(today.year, today.month, today.day, tzinfo=our_timezone)}')
    index = 2
    for category in categories:
        logger.info(f'STARTING GET ACCEPTANCES FOR CATEGORY {category}')
        products = Products.objects.filter(category=category)
        logger.info(f'PRODUCTS - {products}')
        acceptances = Acceptance.objects.filter(product__in=products,
                                                acceptance_date__range=[
                                                    today, today + timedelta(1)
                                                ])
        logger.info(f'ACCEPTANCES - {acceptances}')
        for acceptance in acceptances:
            result = [acceptance.acceptance_date, acceptance.employee.name] + [0]*len(categories)
            result[index] = acceptance.product.name
            logger.info(f'RESULT WAS ADDED {result}')
            results.append(result)
        index += 1
    results = sorted(results, key=lambda x: x[0], reverse=True)
    context['head_row'] = head_row
    context['results'] = results
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
            time_now = datetime.now()
            before_time = time_now - timedelta(minutes=2)
            check_duplicate = Acceptance.objects.filter(
                employee=employee,
                product=product,
                acceptance_date__range=[before_time, time_now]
            )
            if check_duplicate:
                messages.error(request,
                               f'Такая приемка уже создана {check_duplicate[0].acceptance_date.astimezone(our_timezone).strftime("%d.%m.%Y %H:%M")}')
                return redirect('home')
            new_acceptance = Acceptance.objects.create(
                employee=employee,
                product=product
            )
            logger.info(f'NEW ACCEPTANCE WAS CREATED - {new_acceptance}')
            messages.success(request, f'Создана новая приемка изделия')
            return redirect('home')
        else:
            logger.info(f'FORM ERRORS - {form.errors}')
            context['form'] = form
            messages.error(request, 'Допущена ошибка. Проверьте форму')
            return render(request, 'otk/add_acceptance.html', context)
    form = CreateAcceptanceForm()
    context['form'] = form
    return render(request, 'otk/add_acceptance.html', context)


def acceptance_list(request):
    context = {
        'title': 'Редактировать данные внесенные ранее'
    }
    if request.POST:
        form = AcceptanceFilterForm(request.POST)
        logger.info(f'REQUEST DATA - {request.POST}')
        if form.is_valid():
            form_data = form.cleaned_data
            logger.info(f'ACCEPTANCE LIST FORM DATA - {form_data}')
            employees = Employees.objects.filter(id__in=form_data['employee'])
            logger.info(f'EMPLOYEES - {employees}')
            start_date = form_data['start_date']
            end_date = form_data['end_date']
            end_date = datetime(end_date.year, end_date.month, end_date.day)
            logger.info(f'end_date - {datetime(end_date.year, end_date.month, end_date.day, tzinfo=our_timezone)}')
            end_date = end_date + timedelta(1)
            acceptances = Acceptance.objects.filter(acceptance_date__range=[start_date, end_date],
                                                    employee__in=employees).order_by('-acceptance_date')
            logger.info(f'FILTRED ACCEPTANCES {start_date} - {end_date} / {acceptances}')
        else:
            form_data = form.cleaned_data
            logger.info(f'INVALID FORM')
            logger.info(f'ACCEPTANCE LIST FORM DATA - {form_data}')
            logger.info(f'ERRORS - {form.errors}')
            acceptances = None
    else:
        end_date = datetime.today()
        start_date = end_date - timedelta(days=14)
        employees = Employees.objects.all()
        form = AcceptanceFilterForm(
            initial={
                'start_date': start_date,
                'end_date': end_date,
                'employees': employees
            }
        )
        logger.info(f'FIRST form - {form.data}')
        acceptances = Acceptance.objects.filter(acceptance_date__range=[start_date, end_date]).order_by('-acceptance_date')
        logger.info(f'ALL ACCEPTANCES FOR DATERANGE {start_date} - {end_date} / {acceptances}')
    context['form'] = form
    context['acceptances'] = acceptances
    return render(request, 'otk/acceptance_list.html', context)


def report_by_employee(request, employee_id):
    request.session['initial_data'] = employee_id
    return redirect(report)


def report(request):
    context = {
        'title': 'Отчет за период (Ведомость)'
    }
    if request.POST:
        form = ReportFilterForm(request.POST)
        logger.info(f'REQUEST DATA - {request.POST}')
        if form.is_valid():
            form_data = form.cleaned_data
            for i in form_data['products']:
                if i.startswith('category'):
                    form_data['products'].remove(i)
            logger.info(f'ACCEPTANCE LIST FORM DATA - {form_data}')
            employees = Employees.objects.filter(id__in=form_data['employee'])
            logger.info(f'EMPLOYEES - {employees}')
            start_date = form_data['start_date']
            end_date = form_data['end_date']
            # acceptances = Acceptance.objects.filter(acceptance_date__range=[start_date, end_date],
            #                                         employee__in=employees)
            products = Products.objects.filter(id__in=form_data['products'])
            logger.info(f'PRODUCTS {len(products)} {products} - {employees}')
            # logger.info(f'FILTRED ACCEPTANCES {start_date} - {end_date} / {acceptances}')
        else:
            form_data = form.cleaned_data
            logger.info(f'INVALID FORM')
            logger.info(f'ACCEPTANCE LIST FORM DATA - {form_data}')
            logger.info(f'ERRORS - {form.errors}')
            acceptances = None
            return render(request, 'otk/report.html', context)
    else:
        initial_data = request.session.get('initial_data')
        logger.info(f'SESSION INIT DATA - {initial_data}')
        logger.info(f'SESSION EMPLOYEE ID - {request.session}')
        end_date = datetime.today()
        start_date = end_date - timedelta(days=14)
        if not initial_data:
            employees = Employees.objects.all()
        else:
            employees = Employees.objects.filter(id=initial_data)
            logger.info(f'EMPLOYEES - {employees}')
        products = None
        form = ReportFilterForm(
            initial={
                'start_date': start_date,
                'end_date': end_date,
                'employees': employees,
                # 'products': products
            }
        )
        if initial_data:
            del request.session['initial_data']
        logger.info(f'SESSION AFTER REMOVE - {request.session.get("initial_data")}')
        # logger.info(f'FIRST form - {form.data}')
    context['form'] = form
    get_results_response = get_results(start_date, end_date, employees, products)
    if get_results_response:
        head_row, results, final_row = get_results_response
    else:
        messages.error(request, 'Заполните стоимость для всех категорий')
        return redirect('products_catalog')
    context['head_row'] = head_row
    context['results'] = results
    context['final_row'] = final_row
    return render(request, 'otk/report.html', context)


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


def download_acceptances(request):
    logger.info(f'STARTING DOWNLOAD ACCEPTANCES - {request.GET} / {request.GET.urlencode}')
    if request.GET:
        employees = request.GET.getlist('employee')
        start_date = datetime.strptime(request.GET['start_date'], '%d.%m.%Y')
        end_date = datetime.strptime(request.GET['end_date'], '%d.%m.%Y')
    else:
        end_date = datetime.today()
        start_date = end_date - timedelta(days=14)
        employees = Employees.objects.all()
    end_date = datetime(end_date.year, end_date.month, end_date.day)
    logger.info(f'end_date - {datetime(end_date.year, end_date.month, end_date.day, tzinfo=our_timezone)}')
    end_date = end_date + timedelta(1)
    logger.info(f'EMP - {employees}, SD - {start_date}, ED - {end_date}')
    result_queryset = Acceptance.objects.filter(
        acceptance_date__range=[start_date, end_date],
        employee_id__in=employees
    )
    logger.info(f'QS - {result_queryset}')
    data = [['Время', 'Сотрудник', 'Категория', 'Изделие']] + \
           [[i.acceptance_date.astimezone(our_timezone).strftime('%d.%m.%Y %H:%M'), i.employee.name, i.product.category.name, i.product.name] for i in result_queryset]
    logger.info(f'DATA - {data}')
    return ExcelResponse(data, 'Results acceptances')


def autodownload_acceptances(period=30):
    end_date = datetime.today()
    start_date = end_date - timedelta(days=period)
    employees = Employees.objects.all()
    end_date = datetime(end_date.year, end_date.month, end_date.day)
    logger.info(f'end_date - {datetime(end_date.year, end_date.month, end_date.day, tzinfo=our_timezone)}')
    end_date = end_date + timedelta(1)
    logger.info(f'EMP - {employees}, SD - {start_date}, ED - {end_date}')
    result_queryset = Acceptance.objects.filter(
        acceptance_date__range=[start_date, end_date],
        employee_id__in=employees
    )
    logger.info(f'QS - {result_queryset}')
    data = [['Время', 'Сотрудник', 'Категория', 'Изделие']] + \
           [[i.acceptance_date.astimezone(our_timezone).strftime('%d.%m.%Y %H:%M'), i.employee.name,
             i.product.category.name, i.product.name] for i in result_queryset]
    logger.info(f'DATA - {data}')
    df = pd.DataFrame(data)
    df.to_excel(f'{BASE_DIR}/backups/backup-{datetime.today().strftime("%d.%m.%Y")}.xlsx', index=False, header=False)
    return 'Done'



def download_report(request):
    logger.info(f'STARTING DOWNLOAD REPORT - {request.GET} / {request.GET.urlencode}')
    if request.GET:
        employees = Employees.objects.filter(id__in=request.GET.getlist('employee'))
        logger.info(f'EMPLOYEES - {employees}')
        start_date = datetime.strptime(request.GET['start_date'], '%d.%m.%Y')
        end_date = datetime.strptime(request.GET['end_date'], '%d.%m.%Y')
        products_id = []
        for i in request.GET.getlist('products'):
            if not i.startswith('category'):
                products_id.append(i)
        products = Products.objects.filter(id__in=products_id)
        logger.info(f'REQ PRODUCTS - {request.GET.getlist("products")}')
        logger.info(f'PRODUCTS - {products}')
    else:
        end_date = datetime.today()
        start_date = end_date - timedelta(days=14)
        employees = Employees.objects.all()
        products = None
    # head_row, results, final_row = get_results(start_date, end_date, employees, products)
    get_results_response = get_results(start_date, end_date, employees, products)
    if get_results_response:
        head_row, results, final_row = get_results_response
    else:
        messages.error(request, 'Заполните стоимость для всех категорий')
        return redirect('products_catalog')
    logger.info(f'EMP - {employees}, SD - {start_date}, ED - {end_date}')
    data = [head_row] + results + [final_row]
    logger.info(f'DATA - {data}')
    return ExcelResponse(data, 'Results report')


if __name__ == '__main__':
    autodownload_acceptances()



