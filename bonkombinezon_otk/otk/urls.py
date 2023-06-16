from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('login_page', views.login_page, name='login_page'),
    path('login', views.user_login, name='login'),
    path('register', views.user_register, name='register'),
    path('logout', views.user_logout, name='logout'),
    path('admin_page', views.admin_page, name='admin_page'),
    path('add_acceptance', views.add_acceptance, name='add_acceptance'),
    path('products_catalog', views.products_catalog, name='products_catalog'),
    path('create_category', views.CreateCategory.as_view(), name='create_category'),
    path('edit_category/<int:pk>', views.EditCategory.as_view(), name='edit_category'),
    path('delete_category/<int:pk>', views.DeleteCategory.as_view(), name='delete_category'),
    path('create_product', views.CreateProduct.as_view(), name='create_product'),
    path('edit_product/<int:pk>', views.EditProduct.as_view(), name='edit_product'),
    path('delete_product/<int:pk>', views.DeleteProduct.as_view(), name='delete_product'),
    path('load_products', views.load_products, name='load_products'),
    # path('load_products_form', views.load_products_form, name='load_products_form')

    # path('categories/<int:pk>'), views.

]