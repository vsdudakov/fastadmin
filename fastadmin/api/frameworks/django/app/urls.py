import re

from django.urls import path, re_path
from django.views.static import serve

from fastadmin.settings import ROOT_DIR

from .api import (
    action,
    add,
    change,
    change_password,
    configuration,
    dashboard_widget,
    delete,
    export,
    get,
    list_objs,
    me,
    sign_in,
    sign_out,
)
from .views import index


def get_admin_urls():
    return (
        [
            path("", index),
            path("api/sign-in", sign_in),
            path("api/sign-out", sign_out),
            path("api/me", me),
            path("api/dashboard-widget/<str:model>", dashboard_widget),
            path("api/list/<str:model>", list_objs),
            path("api/retrieve/<str:model>/<str:id>", get),
            path("api/add/<str:model>", add),
            path("api/change-password/<str:id>", change_password),
            path("api/change/<str:model>/<str:id>", change),
            path("api/export/<str:model>", export),
            path("api/delete/<str:model>/<str:id>", delete),
            path("api/action/<str:model>/<str:action>", action),
            path("api/configuration", configuration),
            re_path(
                r"^%s(?P<path>.*)$" % re.escape("static"),  # noqa: UP031
                serve,
                kwargs={"document_root": ROOT_DIR / "static"},
            ),
        ],
        "admin",
        "FastAdmin",
    )
