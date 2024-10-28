# myapp/context_processors.py
from datetime import datetime
from babel.dates import format_datetime
from .models import Notification


def current_date(request):
    my_current_date = datetime.now().date()
    day_of_week = format_datetime(my_current_date, 'EEEE', locale='uk_UA')
    date_string = my_current_date.strftime('%Y-%m-%d')
    return {
        'my_current_date': my_current_date,
        'day_of_week': day_of_week,
        'date_string': date_string
    }


# def current_date(request):
#     my_current_date = datetime(2024, 5, 14).date()  # Встановлюємо дату 14 травня 2024 року
#    day_of_week = format_datetime(my_current_date, 'EEEE', locale='uk_UA')
#    date_string = my_current_date.strftime('%Y-%m-%d')
#   return {
#       'my_current_date': my_current_date,
#      'day_of_week': day_of_week,
#      'date_string': date_string
#   }


def display_notifications(request):
    notifications = Notification.objects.all().order_by('-created_at')
    return {'notifications': notifications}
