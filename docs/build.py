import inspect
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from django.apps import apps
from django.apps.registry import Apps
from htmlmin import minify
from jinja2 import Environment, FileSystemLoader, select_autoescape

from fastadmin.settings import ROOT_DIR, Settings
from tests.settings import ROOT_DIR as TESTS_ROOT_DIR

os.environ.setdefault("ADMIN_ENV_FILE", str(ROOT_DIR / "example.env"))
sys.path.append(str(TESTS_ROOT_DIR / "environment" / "django" / "dev"))

Apps.check_apps_ready = lambda x: None


class App:
    label = "app"


apps.get_containing_app_config = lambda x: App()


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
            "version": "0.1.41",
            "changes": [
                "Fixed bug with datetime. Added verbose name logic for models and inlines. Updated frontend libraries.",
            ],
        },
        {
            "version": "0.1.40",
            "changes": [
                "Added RUFF linter. Cleaned up code. Removed pydantic dependency.",
            ],
        },
        {
            "version": "0.1.39",
            "changes": [
                "Bug fixes.",
            ],
        },
        {
            "version": "0.1.38",
            "changes": [
                "Bug fixes.",
            ],
        },
        {
            "version": "0.1.37",
            "changes": [
                "Bug fixes.",
            ],
        },
        {
            "version": "0.1.36",
            "changes": [
                "Added autogeneration of documentation and examples.",
            ],
        },
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
        {
            "version": "0.2.0",
            "changes": [
                "Update packages. Use vite instead obsolete react-scripts.",
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
            ],
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
                    "name": "Chart Types",
                    "url": "#widget-chart-types",
                },
            ],
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
                    "name": "Form Field Types",
                    "url": "#model-form-field-types",
                },
            ],
        },
        {
            "name": "Inline Model Admins",
            "url": "#inline-admins",
            "children": [
                {
                    "name": "Registering Inlines",
                    "url": "#registering-inlines",
                },
                {
                    "name": "Methods and Attributes",
                    "url": "#inline-methods-and-attributes",
                },
            ],
        },
        {
            "name": "Changelog",
            "url": "#changelog",
            "children": [
                {
                    "name": f"v{version['version']}",
                    "url": f"#v{version['version'].replace('.', '_')}",
                }
                for version in versions
            ],
        },
    ]


def get_page_context(page_url):
    from examples.dashboard import djangoorm as dashboard_djangoorm
    from examples.dashboard import tortoise as dashboard_tortoise
    from examples.inlines import tortoise as inlines_tortoise
    from examples.models import tortoise as models_tortoise
    from examples.quick_tutorial import django as quick_tutorial_django
    from examples.quick_tutorial import djangoorm as quick_tutorial_djangoorm
    from examples.quick_tutorial import fastapi as quick_tutorial_fastapi
    from examples.quick_tutorial import flask as quick_tutorial_flask
    from examples.quick_tutorial import ponyorm as quick_tutorial_ponyorm
    from examples.quick_tutorial import sqlalchemy as quick_tutorial_sqlalchemy
    from examples.quick_tutorial import tortoise as quick_tutorial_tortoise

    from fastadmin import DashboardWidgetAdmin, DashboardWidgetType, InlineModelAdmin, ModelAdmin, WidgetType
    from fastadmin.models.base import BaseModelAdmin

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
                    "content": "Note: For zsh and macos use: <code>pip install fastadmin[fastapi,django]</code>",
                },
                {
                    "type": "code-bash",
                    "content": """
pip install fastadmin[fastapi,django]  # for fastapi with django orm
pip install fastadmin[fastapi,tortoise-orm]  # for fastapi with tortoise orm
pip install fastadmin[fastapi,pony]  # for fastapi with pony orm
pip install fastadmin[fastapi,sqlalchemy]  # for fastapi with sqlalchemy orm
pip install fastadmin[django]  # for django with django orm
pip install fastadmin[django,pony]  # for django with pony orm
pip install fastadmin[flask,sqlalchemy]  # for flask with sqlalchemy
""",
                },
                {
                    "type": "text",
                    "content": "Install the package using poetry:",
                },
                {
                    "type": "code-bash",
                    "content": """
poetry add 'fastadmin[fastapi,django]'  # for fastapi with django orm
poetry add 'fastadmin[fastapi,tortoise-orm]'  # for fastapi with tortoise orm
poetry add 'fastadmin[fastapi,pony]'  # for fastapi with pony orm
poetry add 'fastadmin[fastapi,sqlalchemy]'  # for fastapi with sqlalchemy orm
poetry add 'fastadmin[django]'  # for django with django orm
poetry add 'fastadmin[django,pony]'  # for django with pony orm
poetry add 'fastadmin[flask,sqlalchemy]'  # for flask with sqlalchemy
""",
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
                    "content": """
export ADMIN_USER_MODEL=User
export ADMIN_USER_MODEL_USERNAME_FIELD=username
export ADMIN_SECRET_KEY=secret_key
""",
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
                    "id": "setup_framework",
                    "content": [
                        {
                            "name": "FastAPI",
                            "id": "fastapi",
                            "content": [{"type": "code-python", "content": inspect.getsource(quick_tutorial_fastapi)}],
                        },
                        {
                            "name": "Django",
                            "id": "django",
                            "content": [{"type": "code-python", "content": inspect.getsource(quick_tutorial_django)}],
                        },
                        {
                            "name": "Flask",
                            "id": "flask",
                            "content": [{"type": "code-python", "content": inspect.getsource(quick_tutorial_flask)}],
                        },
                    ],
                },
                {
                    "type": "text-lead",
                    "content": "Register ORM models",
                },
                {
                    "type": "tabs",
                    "id": "register_orm_models",
                    "content": [
                        {
                            "name": "Tortoise ORM",
                            "id": "tortoise_orm",
                            "content": [{"type": "code-python", "content": inspect.getsource(quick_tutorial_tortoise)}],
                        },
                        {
                            "name": "Django ORM",
                            "id": "django_orm",
                            "content": [
                                {"type": "code-python", "content": inspect.getsource(quick_tutorial_djangoorm)}
                            ],
                        },
                        {
                            "name": "SQL Alchemy",
                            "id": "sql_alchemy",
                            "content": [
                                {"type": "code-python", "content": inspect.getsource(quick_tutorial_sqlalchemy)}
                            ],
                        },
                        {
                            "name": "Pony ORM",
                            "id": "pony_orm",
                            "content": [{"type": "code-python", "content": inspect.getsource(quick_tutorial_ponyorm)}],
                        },
                    ],
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
                {"type": "code-python", "content": inspect.getsource(Settings)},
                {
                    "type": "alert-warning",
                    "content": "Note: Settings without default values are required.",
                },
            ]
        # widgets
        case "#registering-widgets":
            return [
                {
                    "type": "text-lead",
                    "content": "Register Dashboard widgets",
                },
                {
                    "type": "tabs",
                    "id": "register_dashboard_widgets",
                    "content": [
                        {
                            "name": "Tortoise ORM",
                            "id": "dashboard_tortoise_orm",
                            "content": [{"type": "code-python", "content": inspect.getsource(dashboard_tortoise)}],
                        },
                        {
                            "name": "Django ORM",
                            "id": "dashboard_django_orm",
                            "content": [{"type": "code-python", "content": inspect.getsource(dashboard_djangoorm)}],
                        },
                        {
                            "name": "SQL Alchemy",
                            "id": "dashboard_sql_alchemy",
                            "content": [{"type": "code-python", "content": "See example for Tortoise ORM"}],
                        },
                        {
                            "name": "Pony ORM",
                            "id": "dashboard_pony_orm",
                            "content": [{"type": "code-python", "content": "See example for Tortoise ORM"}],
                        },
                    ],
                },
            ]
        case "#widget-methods-and-attributes":
            return [
                {
                    "type": "text",
                    "content": "There are methods and attributes for Dashboard Widget Admin:",
                },
                {"type": "code-python", "content": inspect.getsource(DashboardWidgetAdmin)},
                {
                    "type": "alert-warning",
                    "content": "Note: Please see <a href='https://charts.ant.design/en/examples' target='_blank'>antd charts</a> for <code>x_field_filter_widget_props</code>.",
                },
            ]
        case "#widget-chart-types":
            return [
                {
                    "type": "text",
                    "content": "There are widget types which fastadmin dashboard supports:",
                },
                {"type": "code-python", "content": inspect.getsource(DashboardWidgetType)},
                {
                    "type": "alert-warning",
                    "content": "Note: Please see <a href='https://charts.ant.design/en/examples' target='_blank'>antd charts</a> for more details (e.g. to see how they look like).",
                },
            ]
        # models
        case "#registering-models":
            return [
                {
                    "type": "tabs",
                    "id": "register_models",
                    "content": [
                        {
                            "name": "Tortoise ORM",
                            "id": "models_tortoise_orm",
                            "content": [{"type": "code-python", "content": inspect.getsource(models_tortoise)}],
                        },
                        {
                            "name": "Django ORM",
                            "id": "models_django_orm",
                            "content": [{"type": "alert-info", "content": "See example for Tortoise ORM"}],
                        },
                        {
                            "name": "SQL Alchemy",
                            "id": "models_sql_alchemy",
                            "content": [{"type": "alert-info", "content": "See example for Tortoise ORM"}],
                        },
                        {
                            "name": "Pony ORM",
                            "id": "models_pony_orm",
                            "content": [{"type": "alert-info", "content": "See example for Tortoise ORM"}],
                        },
                    ],
                },
            ]
        case "#authentication":
            return [
                {
                    "type": "alert-info",
                    "content": "You have to implement methods authenticate and change_password in Modal Admin for User model. See example above.",
                },
            ]
        case "#model-methods-and-attributes":
            return [
                {
                    "type": "text",
                    "content": "There are methods and attributes for Model Admin:",
                },
                {"type": "code-python", "content": inspect.getsource(BaseModelAdmin)},
                {
                    "type": "text",
                    "content": "Specific methods and attributes for Model Admin:",
                },
                {"type": "code-python", "content": inspect.getsource(ModelAdmin)},
            ]
        case "#model-form-field-types":
            return [
                {
                    "type": "text",
                    "content": "There are form field types for model admin:",
                },
                {"type": "code-python", "content": inspect.getsource(WidgetType)},
                {
                    "type": "alert-warning",
                    "content": "Note: Please see <a href='https://ant.design/components/overview' target='_blank'>antd components</a> for more details (e.g. to see how they look like).",
                },
            ]
        # inlines
        case "#registering-inlines":
            return [
                {
                    "type": "tabs",
                    "id": "register_inlines",
                    "content": [
                        {
                            "name": "Tortoise ORM",
                            "id": "inlines_tortoise_orm",
                            "content": [{"type": "code-python", "content": inspect.getsource(inlines_tortoise)}],
                        },
                        {
                            "name": "Django ORM",
                            "id": "inlines_django_orm",
                            "content": [{"type": "alert-info", "content": "See example for Tortoise ORM"}],
                        },
                        {
                            "name": "SQL Alchemy",
                            "id": "inlines_sql_alchemy",
                            "content": [{"type": "alert-info", "content": "See example for Tortoise ORM"}],
                        },
                        {
                            "name": "Pony ORM",
                            "id": "inlines_pony_orm",
                            "content": [{"type": "alert-info", "content": "See example for Tortoise ORM"}],
                        },
                    ],
                },
            ]
        case "#inline-methods-and-attributes":
            return [
                {
                    "type": "text",
                    "content": "There are methods and attributes for Inline Model Admin:",
                },
                {
                    "type": "alert-info",
                    "content": "See BaseModelAdmin class methods and attributes in model admin section.",
                },
                {
                    "type": "text",
                    "content": "Specific methods and attributes for Inline Model Admin:",
                },
                {"type": "code-python", "content": inspect.getsource(InlineModelAdmin)},
            ]
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
                            }
                            for change in v["changes"]
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
        "year": datetime.now(timezone.utc).year,
        "created_date": "7 March 2023",
        "updated_date": datetime.now(timezone.utc).strftime("%d %B %Y"),
        "github_url": GITHUB_URL,
        "pypi_url": PYPI_URL,
        "versions": get_versions(),
        "sections": get_sections(),
        "get_page_context": get_page_context,
    }


def build():
    env = Environment(loader=FileSystemLoader("."), autoescape=select_autoescape())
    context = get_context()

    index_template = env.get_template("templates/index.html")
    index_html = index_template.render(**context)
    with Path.open(Path("index.html"), "w") as fh:
        fh.write(minify(index_html))

    readme_template = env.get_template("templates/readme.md")
    readme_md = readme_template.render(**context)
    with Path.open(Path(ROOT_DIR / ".." / "README.md"), "w") as fh:
        fh.write(readme_md)


if __name__ == "__main__":
    build()
