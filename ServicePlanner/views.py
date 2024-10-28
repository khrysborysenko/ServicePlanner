from django.shortcuts import render, redirect, get_object_or_404
import datetime
from datetime import date
from datetime import datetime, timedelta
from django.contrib import messages
from django.views.generic import FormView
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from .models import Resource, Service, ServiceResource, Notification
from .models import Customer, ServiceHistory, FutureServices
from .forms import CustomerForm, ServiceHistoryForm, ReplenishForm, FutureServiceForm, PeriodForm
from django.db.models import Count
import matplotlib.pyplot as plt
import io
import base64
import colorsys
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseRedirect
from .utils import perform_clustering, recommend_services_for_customer


class RegisterView(FormView):
    template_name = 'ServicePlanner//register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


def resource_list(request):
    resources = Resource.objects.all()
    services = Service.objects.prefetch_related('serviceresource_set__resource').all()
    customers = Customer.objects.all()
    return render(request, 'ServicePlanner/home.html',
                  {'resources': resources, 'services': services, 'customers': customers})


def resource_storage(request):
    resources = Resource.objects.all()
    return render(request, 'ServicePlanner/resource_storage.html', {'resources': resources})


def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'ServicePlanner/customer_list.html', {'customers': customers})


def customer_edit(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'ServicePlanner/customer_edit.html', {'form': form})


def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'ServicePlanner/add_customer.html', {'form': form})


def delete_customer(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Клієнт був успішно видалений')
        return redirect('customer_list')
    return render(request, 'ServicePlanner/delete_customer.html', {'customer': customer})


def create_service_history(request, service_id):
    service = Service.objects.get(id=service_id)
    if request.method == 'POST':
        form = ServiceHistoryForm(request.POST)
        if form.is_valid():
            form.instance.service = service
            form.save()

            service_resources = ServiceResource.objects.filter(service=service)
            for service_resource in service_resources:
                resource = service_resource.resource
                resource.quantity -= service_resource.quantity
                resource.save()
            return redirect('/service-history/')

    else:

        initial_data = {'date': date.today(), 'service': service}
        form = ServiceHistoryForm(initial=initial_data)
        return render(request, 'ServicePlanner/create_service_history.html', {'form': form})


def servicehistory_list(request):
    service_history = ServiceHistory.objects.all()
    return render(request, 'ServicePlanner/servicehistory_list.html', {'service_history': service_history})


def replenish_resource(request, resource_id):
    resource = Resource.objects.get(pk=resource_id)
    if request.method == 'POST':
        form = ReplenishForm(request.POST)
        if form.is_valid():
            quantity_to_add = form.cleaned_data['quantity']
            resource.quantity += quantity_to_add
            resource.save()
            return redirect('/resources/',
                            resource_id=resource_id)
    else:
        form = ReplenishForm()
    return render(request, 'ServicePlanner/replenish_resource.html', {'form': form})


def calendar(request):
    # Встановлюємо початкову дату на 12 травня 2024 року
    today = datetime.now().date()

    start_date = today - timedelta(days=today.weekday())
    weeks = []

    days_of_week = ['Понеділок', 'Вівторок', 'Середа', 'Четвер', 'П\'ятниця', 'Субота', 'Неділя']

    for i in range(4):  # Генеруємо 4 тижні
        week = []
        for j in range(7):  # 7 днів у тижні
            day_of_week = start_date.strftime('%A')
            week.append((start_date, day_of_week))
            start_date += timedelta(days=1)
        weeks.append(week)

    plans = FutureServices.objects.all()

    return render(request, 'ServicePlanner/calendar.html', {'weeks': weeks, 'days_of_week': days_of_week,
                                                            'plans': plans})


def add_future_service(request):
    if request.method == 'POST':
        form = FutureServiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/calendar/')

    else:
        form = FutureServiceForm()
        return render(request, 'ServicePlanner/add_future_service.html', {'form': form})


def period_view(request):
    if request.method == 'POST':
        form = PeriodForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            img1 = io.BytesIO()
            img2 = io.BytesIO()
            plot_service_percentage(start_date, end_date, img1, img2)
            img1.seek(0)
            img2.seek(0)
            plot_url1 = base64.b64encode(img1.getvalue()).decode()
            plot_url2 = base64.b64encode(img2.getvalue()).decode()

            start_date_str = request.POST.get('start_date', '')
            end_date_str = request.POST.get('end_date', '')

            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

            period_name = start_date.strftime('%Y-%m-%d') + '_' + end_date.strftime('%Y-%m-%d')

            return render(request, 'ServicePlanner/analytics.html',
                          {'form': form, 'plot_url1': plot_url1, 'plot_url2': plot_url2, 'period_name': period_name})
    else:
        form = PeriodForm()

    return render(request, 'ServicePlanner/analytics.html', {'form': form})


def plot_service_percentage(start_date, end_date, buffer_bar, buffer_pie):

    service_counts = ServiceHistory.objects.filter(date__range=(start_date, end_date)) \
                                           .values('service__name') \
                                           .annotate(count=Count('service'))

    labels = []
    counts = []

    for entry in service_counts:
        labels.append(entry['service__name'])
        counts.append(entry['count'])
    bar_color = (125 / 255, 232 / 255, 232 / 255)

    plt.figure(figsize=(10, 6))
    plt.bar(labels, counts, color=bar_color)
    plt.xlabel('Послуги')
    plt.ylabel('Кількість')
    plt.title('Статистика виконаних послуг')

    plt.xticks(rotation=45, ha='right')

    plt.tight_layout()
    plt.savefig(buffer_bar, format='png')
    plt.close()

    num_colors = len(labels)
    hsl_colors = [(i / num_colors, 0.7, 0.7) for i in
                  range(num_colors)]

    rgb_colors = [colorsys.hls_to_rgb(*hsl) for hsl in hsl_colors]

    plt.figure(figsize=(8, 6))
    plt.pie(counts, labels=labels, autopct='%1.1f%%', startangle=140, colors=rgb_colors)
    plt.axis('equal')
    plt.title('Percentage of Services Performed')

    plt.tight_layout()
    plt.savefig(buffer_pie, format='png')
    plt.close()


@require_http_methods(["DELETE"])
def delete_notification(request, notification_id):
    try:
        notification = Notification.objects.get(pk=notification_id)
        notification.delete()
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False}, status=404)


def reload_page(request):
    current_url = request.build_absolute_uri()
    return HttpResponseRedirect(current_url)


def my_view(request):
    perform_clustering()
    customer_id = 3
    recommended_services = recommend_services_for_customer(customer_id)

    context = {
        'recommended_services': recommended_services
    }

    return render(request, 'ServicePlanner/recommendations.html', context)
