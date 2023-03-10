import os

from django.conf.urls.static import static
from django.urls import path

from fastadmin.settings import ROOT_DIR

from .api import configuration, sign_in, sign_out, me, list, get, add, change, export, delete, action
from .views import index


def get_admin_urls():
    return (
        [
            path("", index),
            path("api/sign-in", sign_in),
            path("api/sign-out", sign_out),
            path("api/me", me),
            path("api/list/<str:model>", list),
            path("api/retrieve/<str:model>/<str:id>", get),
            path("api/add/<str:model>", add),
            path("api/change/<str:model>/<str:id>", change),
            path("api/export/<str:model>", export),
            path("api/delete/<str:model>/<str:id>", delete),
            path("api/action/<str:model>/<str:action>", action),
            path("api/configuration", configuration),
        ]
        + static("static", document_root=os.path.join(ROOT_DIR, "static")),
        "admin",
        "FastAdmin",
    )
