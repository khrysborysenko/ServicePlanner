from django import forms
from .models import Customer, ServiceHistory, Service


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'email', 'phone_number']


class ServiceHistoryForm(forms.ModelForm):
    class Meta:
        model = ServiceHistory
        fields = ['client', 'service', 'date']

    def __init__(self, *args, **kwargs):
        super(ServiceHistoryForm, self).__init__(*args, **kwargs)
        self.fields['client'].queryset = Customer.objects.all()


class FutureServiceForm(forms.ModelForm):
    class Meta:
        model = ServiceHistory
        fields = ['client', 'service', 'date']

    def __init__(self, *args, **kwargs):
        super(FutureServiceForm, self).__init__(*args, **kwargs)
        self.fields['client'].queryset = Customer.objects.all()
        self.fields['service'].queryset = Service.objects.all()
        self.fields['date'].queryset = Service.objects.all()


class ReplenishForm(forms.Form):
    quantity = forms.IntegerField(label='Кількість для поповнення')


class PeriodForm(forms.Form):
    start_date = forms.DateField(label='Start Date', widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(label='End Date', widget=forms.DateInput(attrs={'type': 'date'}))
