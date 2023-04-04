from django.urls import path

from fastadmin import get_django_admin_urls as get_admin_urls
from fastadmin.settings import settings

urlpatterns = [
    path(f"{settings.ADMIN_PREFIX}/", get_admin_urls()),
]
