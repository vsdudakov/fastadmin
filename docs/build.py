from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import date
from htmlmin import minify
import inspect
import django

import os
import sys
from tests.settings import ROOT_DIR

sys.path.append(os.path.join(ROOT_DIR, "..", "examples", "django", "dev"))  # for dev.settings
sys.path.append(os.path.join(ROOT_DIR, "..", "examples"))  # for djangoorm

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dev.settings")
os.environ.setdefault("ADMIN_ENV_FILE", os.path.join(os.path.dirname(__file__), "..", "example.env"))

django.setup(set_prefix=False)

from fastadmin.settings import Settings
from examples.fastapi import app as fastapi_app
from examples.django.dev.dev import urls as django_app
from examples.flask import app as flask_app
from examples.tortoiseorm import models as tortoise_models
from examples.djangoorm import models as django_models
from examples.sqlalchemy import models as sqlalchemy_models
from examples.ponyorm import models as pony_models


GITHUB_URL = "https://github.com/vsdudakov/fastadmin"
PYPI_URL = "https://pypi.org/project/fastadmin/"
NAME = "FastAdmin"
AUTHOR_NAME = "Seva D."
AUTHOR_EMAIL = "vsdudakov@gmail.com"


def read_cls_docstring(cls):
    return cls.__doc__.strip()


def get_versions():
    return [
        {
            "version": "0.1.35",
            "changes": [
                "Added DashboardWidgetAdmin class and charts for dashboard.",
            ],
        },
        {
            "version": "0.1.34",
            "changes": [
                "Added SlugInput, EmailInput, PhoneInput, UrlInput, JsonTextArea widget types.",
            ],
        },
        {
            "version": "0.1.33",
            "changes": [
                "Added list_display_widths parameter.",
            ],
        },
        {
            "version": "0.1.32",
            "changes": [
                "Added Upload widget type.",
            ],
        },
        {
            "version": "0.1.31",
            "changes": [
                "Added PasswordInput widget type.",
            ],
        },
    ]


def get_sections():
    versions = get_versions()
    return [
        {
            "name": "Introduction",
            "url": "#introduction",
        },
        {
            "name": "Getting Started",
            "url": "#getting_started",
            "children": [
                {
                    "name": "Installation",
                    "url": "#installation",
                },
                {
                    "name": "Quick Tutorial",
                    "url": "#quick_tutorial",
                },
            ]
        },
        {
            "name": "Settings",
            "url": "#settings",
        },
        {
            "name": "Dashboard Widget Admins",
            "url": "#dashboard-widget-admins",
            "children": [
                {
                    "name": "Registering Widgets",
                    "url": "#registering-widgets",
                },
                {
                    "name": "Methods and Attributes",
                    "url": "#widget-methods-and-attributes",
                },
                {
                    "name": "Examples",
                    "url": "#widget-examples",
                },
            ]
        },
        {
            "name": "Model Admins",
            "url": "#model-admins",
            "children": [
                {
                    "name": "Registering Models",
                    "url": "#registering-models",
                },
                {
                    "name": "Authentication",
                    "url": "#authentication",
                },
                {
                    "name": "Methods and Attributes",
                    "url": "#model-methods-and-attributes",
                },
                {
                    "name": "Examples",
                    "url": "#model-examples",
                },
            ]
        },
        {
            "name": "Inline Model Admins",
            "url": "#inline-model-admins",
            "children": [
                {
                    "name": "Registering Inlines",
                    "url": "#registering-inlines",
                },
                {
                    "name": "Methods and Attributes",
                    "url": "#inline-methods-and-attributes",
                },
                {
                    "name": "Examples",
                    "url": "#inline-examples",
                },
            ]
        },
        {
            "name": "Changelog",
            "url": "#changelog",
            "children": [
                {
                    "name": f"v{version['version']}",
                    "url": f"#v{version['version'].replace('.', '_')}",
                } for version in versions
            ]
        },

    ]


def get_page_context(page_url):
    match page_url:
        case "#introduction":
            return [
                {
                    "type": "text",
                    "content": f"<a href='{GITHUB_URL}' target='_blank'>FastAdmin</a> is an easy-to-use Admin Dashboard App for FastAPI/Django/Flask inspired by Django Admin.",
                },
                {
                    "type": "text",
                    "content": "FastAdmin was built with relations in mind and admiration for the excellent and popular Django Admin. It's engraved in its design that you may configure your admin dashboard for FastAPI/Django/Flask easiest way.",
                },
                {
                    "type": "text",
                    "content": "FastAdmin is designed to be minimalistic, functional and yet familiar.",
                },
            ]
        case "#getting_started":
            return [
                {
                    "type": "alert-info",
                    "content": f"If you have any questions that are beyond the scope of the documentation, Please feel free to email <a href='mailto:{AUTHOR_EMAIL}' target='_blank'>us</a>.",
                },
            ]
        case "#installation":
            return [
                {
                    "type": "text-lead",
                    "content": f"Follow the steps below to setup {NAME}:",
                },
                {
                    "type": "text",
                    "content": "Install the package using pip:",
                },
                {
                    "type": "alert-info",
                    "content": "Note: For zsh and macos use: <code>pip install fastadmin\[fastapi,django\]</code>",
                },
                {
                    "type": "code-bash",
                    "content":
"""
pip install fastadmin[fastapi,django]  # for fastapi with django orm
pip install fastadmin[fastapi,tortoise-orm]  # for fastapi with tortoise orm
pip install fastadmin[fastapi,pony]  # for fastapi with pony orm
pip install fastadmin[fastapi,sqlalchemy]  # for fastapi with sqlalchemy orm
pip install fastadmin[django]  # for django with django orm
pip install fastadmin[django,pony]  # for django with pony orm
pip install fastadmin[flask,sqlalchemy]  # for flask with sqlalchemy
"""
                },
                {
                    "type": "text",
                    "content": "Install the package using poetry:",
                },
                {
                    "type": "code-bash",
                    "content":
"""
poetry add 'fastadmin[fastapi,django]'  # for fastapi with django orm
poetry add 'fastadmin[fastapi,tortoise-orm]'  # for fastapi with tortoise orm
poetry add 'fastadmin[fastapi,pony]'  # for fastapi with pony orm
poetry add 'fastadmin[fastapi,sqlalchemy]'  # for fastapi with sqlalchemy orm
poetry add 'fastadmin[django]'  # for django with django orm
poetry add 'fastadmin[django,pony]'  # for django with pony orm
poetry add 'fastadmin[flask,sqlalchemy]'  # for flask with sqlalchemy
"""
                },
                {
                    "type": "text",
                    "content": "Configure required settings using virtual environment variables:",
                },
                {
                    "type": "alert-info",
                    "content": "Note: You can add these variables to .env and use python-dotenv to load them. See all settings <a href='#settings'>here</a>",
                },
                {
                    "type": "code-bash",
                    "content":
"""
export ADMIN_USER_MODEL=User
export ADMIN_USER_MODEL_USERNAME_FIELD=username
export ADMIN_SECRET_KEY=secret_key
"""
                },
            ]
        case "#quick_tutorial":
            return [
                {
                    "type": "text-lead",
                    "content": f"Setup {NAME} for a framework",
                },
                {
                    "type": "tabs",
                    "id": f"Setup {NAME} for a framework",
                    "content": [
                        {
                            "name": "FastAPI",
                            "content": [
                                {
                                    "type": "code-python",
                                    "content": inspect.getsource(fastapi_app)
                                }
                            ]
                        },
                        {
                            "name": "Django",
                            "content": [
                                {
                                    "type": "code-python",
                                    "content": inspect.getsource(django_app)
                                }
                            ]
                        },
                        {
                            "name": "Flask",
                            "content": [
                                {
                                    "type": "code-python",
                                    "content": inspect.getsource(flask_app)
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "text-lead",
                    "content": "Register ORM models",
                },
                {
                    "type": "tabs",
                    "id": "Register ORM models",
                    "content": [
                        {
                            "name": "Tortoise ORM",
                            "content": [
                                {
                                    "type": "code-python",
                                    "content": inspect.getsource(tortoise_models)
                                }
                            ]
                        },
                        {
                            "name": "Django ORM",
                            "content": [
                                {
                                    "type": "code-python",
                                    "content": inspect.getsource(django_models)
                                }
                            ]
                        },
                        {
                            "name": "SQL Alchemy",
                            "content": [
                                {
                                    "type": "code-python",
                                    "content": inspect.getsource(sqlalchemy_models)
                                }
                            ]
                        },
                        {
                            "name": "Pony ORM",
                            "content": [
                                {
                                    "type": "code-python",
                                    "content": inspect.getsource(pony_models)
                                }
                            ]
                        }
                    ]
                },
            ]
        # settings
        case "#settings":
            return [
                {
                    "type": "text",
                    "content": "There are settings with default values:",
                },
                {
                    "type": "alert-info",
                    "content": "Note: Export virtual environment variables or create <code>.env</code> file with variables and use <code>python-dotenv</code> package.",
                },
                {
                    "type": "code-python",
                    "content": inspect.getsource(Settings)
                },
                {
                    "type": "alert-warning",
                    "content": "Note: Settings without default values are required.",
                },
            ]
        # widgets
        case "#dashboard-widget-admins":
            return []
        case "#registering-widgets":
            return []
        case "#widget-methods-and-attributes":
            return []
        case "#widget-examples":
            return []
        # models
        case "#model-admins":
            return []
        case "#registering-models":
            return []
        case "#authentication":
            return []
        case "#model-methods-and-attributes":
            return []
        case "#model-examples":
            return []
        # inlines
        case "#inline-admins":
            return []
        case "#registering-inlines":
            return []
        case "#inline-methods-and-attributes":
            return []
        case "#inline-examples":
            return []
        # changelog
        case "#changelog":
            return [
                {
                    "type": "alert-info",
                    "content": "See what's new added, changed, fixed, improved or updated in the latest versions.",
                },
            ]
        case _:
            if page_url.startswith("#v"):
                version = page_url.replace("#v", "").replace("_", ".")
                for v in get_versions():
                    if v["version"] == version:
                        return [
                            {
                                "type": "text",
                                "content": change,
                            } for change in v["changes"]
                        ]
    return []


def get_context():
    return {
        "title": f"{NAME} | Documentation",
        "description": f"{NAME} is an easy-to-use Admin Dashboard App for FastAPI/Django/Flask inspired by Django Admin.",
        "author": {
            "name": AUTHOR_NAME,
            "email": AUTHOR_EMAIL,
        },
        "name": NAME,
        "year": date.today().year,
        "created_date": "7 March 2023",
        "updated_date": date.today().strftime("%d %B %Y"),
        "github_url": GITHUB_URL,
        "pypi_url": PYPI_URL,
        "versions": get_versions(),
        "sections": get_sections(),
        "get_page_context": get_page_context,
    }


def build():
    env = Environment(
        loader=FileSystemLoader("."),
        autoescape=select_autoescape()
    )
    context = get_context()

    index_template = env.get_template("templates/index.html")
    index_html = index_template.render(**context)
    with open("index.html", "w") as fh:
        fh.write(minify(index_html))

    readme_template = env.get_template("templates/readme.md")
    readme_md = readme_template.render(**context)
    with open("README.md", "w") as fh:
        fh.write(readme_md)




if __name__ == "__main__":
    build()
