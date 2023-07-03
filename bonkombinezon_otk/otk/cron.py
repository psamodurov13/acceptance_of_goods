from .views import autodownload_acceptances


def my_scheduled_job():
    autodownload_acceptances()