"""
URL configuration for djangoProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls')
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LoginView
from ServicePlanner.views import resource_list, customer_list, add_customer, delete_customer, customer_edit
from ServicePlanner.views import RegisterView, create_service_history, servicehistory_list, resource_storage
from ServicePlanner.views import replenish_resource, calendar, add_future_service, period_view, delete_notification, reload_page, my_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LoginView.as_view(template_name='ServicePlanner/login.html'), name='login'),
    path('register/', RegisterView.as_view(template_name='ServicePlanner/register.html'), name='register'),
    path('home/', resource_list, name='resource_list'),
    path('customer/', customer_list, name='customer_list'),
    path('customer/add/', add_customer, name='add_customer'),
    path('customer/edit/<int:customer_id>/', customer_edit, name='customer_edit'),
    path('customer/delete/<int:customer_id>/', delete_customer, name='delete_customer'),
    path('create_service_history/<int:service_id>/', create_service_history, name='create_service_history'),
    path('service-history/', servicehistory_list, name='service_history_list'),
    path('calendar/', calendar, name='calendar'),
    path('add_future_service/', add_future_service, name='add_future_service'),
    path('resources/', resource_storage, name='resource_storage'),
    path('replenish_resource/<int:resource_id>/', replenish_resource, name='replenish_resource'),
    path('analytics/', period_view, name='period_view'),
    path('delete-notification/<int:notification_id>/', delete_notification, name='delete_notification'),
    path('reload/', reload_page, name='reload_page'),
    path('recommendations/', my_view, name='recommendations'),
]
