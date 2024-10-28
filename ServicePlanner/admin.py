from django.contrib import admin
from .models import Resource, ServiceResource, Service, FutureServices


class ServiceResourceInline(admin.TabularInline):
    model = ServiceResource
    extra = 1


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'quantity', 'unit_price', 'description']
    search_fields = ['name']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'duration']
    search_fields = ['name']
    inlines = [ServiceResourceInline]


@admin.register(FutureServices)
class FutureServicesAdmin(admin.ModelAdmin):
    list_display = ('client', 'service', 'date')
    search_fields = ('client__name', 'service__name')
    list_filter = ('date', 'service', 'client')