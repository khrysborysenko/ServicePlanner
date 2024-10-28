from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Resource(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()

    def __str__(self) -> str:
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=50)
    resources_required = models.ManyToManyField(Resource, through='ServiceResource')

    def __str__(self):
        return self.name


class ServiceResource(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, default='', blank=True)
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class ServiceHistory(models.Model):
    client = models.ForeignKey('Customer', on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='service_history')
    date = models.DateField()
    similar_services_recommended = models.ManyToManyField(Service, related_name='similar_services_history', blank=True)
    cluster_label = models.IntegerField(null=True, blank=True)


class FutureServices(models.Model):
    client = models.ForeignKey('Customer', on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='future_services')
    date = models.DateField()

    def __str__(self):
        return self.id


class Notification(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.resource.name} - {self.created_at}"


@receiver(post_save, sender=Resource)
def check_resource_quantity(sender, instance, **kwargs):
    threshold = 10  # Задайте поріг, коли потрібно створити повідомлення
    if instance.quantity <= threshold:
        message = f"Потрібно замовити більше {instance.name}. Залишилося лише {instance.quantity} одиниць."
        Notification.objects.create(resource=instance, message=message)
