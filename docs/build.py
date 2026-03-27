import inspect
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from django.apps import apps
from django.apps.registry import Apps
from jinja2 import Environment, FileSystemLoader, select_autoescape

from fastadmin.settings import ROOT_DIR, Settings

os.environ.setdefault("ADMIN_ENV_FILE", str(ROOT_DIR / "example.env"))
# Add project root so example apps (in examples/*) can be imported.
sys.path.append(str(ROOT_DIR.parent))

Apps.check_apps_ready = lambda x: None


def html_minify(html: str) -> str:
    return html.strip()


class App:
    label = "app"


apps.get_containing_app_config = lambda x: App()


GITHUB_URL = "https://github.com/vsdudakov/fastadmin"
PYPI_URL = "https://pypi.org/project/fastadmin/"
NAME = "FastAdmin"
AUTHOR_NAME = "Seva D."
AUTHOR_EMAIL = "vsdudakov@gmail.com"
ANTD_CHARTS_EXAMPLES = "https://ant-design-charts.antgroup.com/en/examples"

PROJECT_ROOT = ROOT_DIR.parent


def read_cls_docstring(cls):
    return cls.__doc__.strip()


def get_versions():
    return [
        {
            "version": "0.4.8",
            "changes": [
                "Add toolbar actions to widget action results.",
                "Add table view to widget action results.",
                "Add JSON view to widget action results.",
                "Enhance a documentation for upload_file method.",
                "Add str type for pk.",
            ],
        },
        {
            "version": "0.4.7",
            "changes": [
                "Add sub_tab to widget action props.",
                "Dark mode support.",
            ],
        },
        {
            "version": "0.4.6",
            "changes": [
                "Add max_height to widget action props.",
                "Add highlight search results to widget action results.",
                "Add copy to clipboard to widget action results.",
                "Add expand results modal to widget action results.",
                "Add menu_section to model admins.",
            ],
        },
        {
            "version": "0.4.5",
            "changes": [
                "Add parent argument to widget action props.",
                "Add wraps to decorator to keep the original function name and docstring.",
                "Add pre_generate_models_schema method to ModelAdmin to pre-generate models schema.",
                "Fix examples.",
            ],
        },
        {
            "version": "0.4.4",
            "changes": ["Replace helmet to update title and description.", "Improve frontend coverage."],
        },
        {
            "version": "0.4.3",
            "changes": ["Add series field to widget action props. Fix examples.", "Add search by actions."],
        },
        {
            "version": "0.4.2",
            "changes": [
                "Replace DashboardWidgetAdmin with widget_action decorator. (no backward compatibility)",
                "Fix mobile view.",
            ],
        },
        {
            "version": "0.4.1",
            "changes": [
                "Fix upload file functionality. Fix examples.",
            ],
        },
        {
            "version": "0.4.0",
            "changes": [
                "Add new upload file functionality (without backward compatibility). See documentation for details.",
                "Add example for flask with sqlalchemy",
                "Removed ADMIN_DISABLE_CROP_IMAGE setting. Use disableCropImage prop in UploadImage widget instead.",
            ],
        },
        {
            "version": "0.3.11",
            "changes": [
                "Fix API service errors.",
            ],
        },
        {
            "version": "0.3.10",
            "changes": [
                "Fix file download issue for actions.",
            ],
        },
        {
            "version": "0.3.9",
            "changes": [
                "Add response types for actions.",
                "Fix Decimal fields handling.",
            ],
        },
        {
            "version": "0.3.8",
            "changes": [
                "Fix inline add/change issue.",
                "Fix inline filter reset issue.",
            ],
        },
        {
            "version": "0.3.7",
            "changes": [
                "Fix filter reset issue.",
                "Fix date/time handling in transform helpers.",
                "Fix examples.",
                "Fix JSON textarea handling.",
            ],
        },
        {
            "version": "0.3.6",
            "changes": [
                "Fix datetime/time handling in transform helpers.",
                "Revert get_orm_list method to original implementation. We can use list_select_related and search_fields for prefetch_related_fields and additional_search_fields.",
            ],
        },
        {
            "version": "0.3.5",
            "changes": [
                "Enhance get_orm_list method to support prefetch_related_fields and additional_search_fields.",
                "Add request/user context on BaseModelAdmin for per-request custom logic.",
            ],
        },
        {
            "version": "0.3.4",
            "changes": [
                "Fix sort by and search by relations. Fix examples.",
            ],
        },
        {
            "version": "0.3.3",
            "changes": [
                "Fix DetachedInstanceError when session is closed after commit.",
                "Fix list display widths.",
                "Fix flask issues.",
            ],
        },
        {
            "version": "0.3.2",
            "changes": [
                "Add formfield_overrides example. Add label and help props.",
            ],
        },
        {
            "version": "0.3.1",
            "changes": [
                "Fix sqlalchemy required fields. Fix CI.",
            ],
        },
        {
            "version": "0.3.0",
            "changes": [
                "Clean up documentation. Update dependencies. Fix linters and tests. Frontend refactoring.",
            ],
        },
        {
            "version": "0.2.22",
            "changes": [
                "Fix upload base64 widget; add disableCropImage prop. Fix examples.",
            ],
        },
        {
            "version": "0.2.21",
            "changes": [
                "Fix cleaning of async select fields on forms.",
            ],
        },
        {
            "version": "0.2.20",
            "changes": [
                "Fix _id fields handling. Bump backend and frontend packages.",
            ],
        },
        {
            "version": "0.2.19",
            "changes": [
                "Fix is_pk for Tortoise ORM.",
            ],
        },
        {
            "version": "0.2.18",
            "changes": [
                "Fix M2M/FK handling for SQLAlchemy with PostgreSQL (convert str to int).",
            ],
        },
        {
            "version": "0.2.17",
            "changes": [
                "Fix FK handling for SQLAlchemy with PostgreSQL (convert str to int).",
            ],
        },
        {
            "version": "0.2.16",
            "changes": [
                "Add ADMIN_DISABLE_CROP_IMAGE setting to configure image cropping on upload.",
            ],
        },
        {
            "version": "0.2.15",
            "changes": [
                "Fix password logic for user model.",
            ],
        },
        {
            "version": "0.2.14",
            "changes": [
                "Make permission functions awaitable. Bump frontend and backend packages.",
            ],
        },
        {
            "version": "0.2.13",
            "changes": [
                "Fix edit page frontend issue for Date field.",
            ],
        },
        {
            "version": "0.2.12",
            "changes": [
                "Remove python-dotenv dependency. Bump Django. Add Django example.",
            ],
        },
        {
            "version": "0.2.11",
            "changes": [
                "Fix examples. Fix Pony ORM (delete, update M2M). Allow sorting by custom columns. Fix list_display ordering.",
            ],
        },
        {
            "version": "0.2.10",
            "changes": [
                "Fix empty M2M issue. Optimize unit tests. Fix Pony ORM. Optimize Tortoise ORM search.",
            ],
        },
        {
            "version": "0.2.9",
            "changes": [
                "Fix modal inline dialogs. Fix M2M multiple select.",
            ],
        },
        {
            "version": "0.2.8",
            "changes": [
                "Fix SQLAlchemy delete functionality. Add more examples.",
            ],
        },
        {
            "version": "0.2.7",
            "changes": [
                "Fix helper functions. Add regex support.",
            ],
        },
        {
            "version": "0.2.6",
            "changes": [
                "Add edit button for async select.",
            ],
        },
        {
            "version": "0.2.5",
            "changes": [
                "Fix async select in inlines.",
            ],
        },
        {
            "version": "0.2.4",
            "changes": [
                "Fix dashboard widgets and auto-register inlines.",
            ],
        },
        {
            "version": "0.2.3",
            "changes": [
                "Fix filter issue on list views. Remove Jinja from dependencies.",
            ],
        },
        {
            "version": "0.2.2",
            "changes": [
                "Fix datetime-related bugs.",
            ],
        },
        {
            "version": "0.2.1",
            "changes": [
                "Update packages. Fix linters and tests in Vite frontend. Remove Pydantic from dependencies.",
            ],
        },
        {
            "version": "0.2.0",
            "changes": [
                "Update packages. Use Vite instead of deprecated react-scripts.",
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
            ],
        },
        {
            "name": "Settings",
            "url": "#settings",
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


def read_example(rel_path: str) -> str:
    """Read example code from the examples/* folder relative to project root."""
    return Path(PROJECT_ROOT / rel_path).read_text()


def get_page_context(page_url):

    from fastadmin import InlineModelAdmin, ModelAdmin, WidgetType, widget_action
    from fastadmin.models.base import BaseModelAdmin
    from fastadmin.models.schemas import (
        WidgetActionArgumentProps,
        WidgetActionChartProps,
        WidgetActionFilter,
        WidgetActionInputSchema,
        WidgetActionProps,
        WidgetActionResponseSchema,
        WidgetActionType,
    )

    match page_url:
        case "#introduction":
            return [
                {
                    "type": "text",
                    "content": f"<a href='{GITHUB_URL}' target='_blank'>FastAdmin</a> is an easy-to-use admin dashboard for FastAPI, Django, and Flask, inspired by Django Admin.",
                },
                {
                    "type": "text",
                    "content": "FastAdmin is built with relationships in mind and admiration for Django Admin. Its design focuses on making it as easy as possible to configure your admin dashboard for FastAPI, Django, or Flask.",
                },
                {
                    "type": "text",
                    "content": "FastAdmin aims to be minimal, functional, and familiar.",
                },
            ]
        case "#getting_started":
            return [
                {
                    "type": "alert-info",
                    "content": f"If you have questions beyond this documentation, feel free to <a href='mailto:{AUTHOR_EMAIL}' target='_blank'>email us</a>.",
                },
            ]
        case "#installation":
            return [
                {
                    "type": "text-lead",
                    "content": f"Follow the steps below to set up {NAME}:",
                },
                {
                    "type": "text",
                    "content": "Install the package with pip:",
                },
                {
                    "type": "alert-info",
                    "content": "On zsh and macOS, use quotes: <code>pip install 'fastadmin[fastapi,django]'</code>",
                },
                {
                    "type": "code-bash",
                    "content": """
pip install fastadmin[fastapi,django]        # FastAPI with Django ORM
pip install fastadmin[fastapi,tortoise-orm]  # FastAPI with Tortoise ORM
pip install fastadmin[fastapi,pony]          # FastAPI with Pony ORM
pip install fastadmin[fastapi,sqlalchemy]    # FastAPI with SQLAlchemy (includes greenlet)
pip install fastadmin[django]                # Django with Django ORM
pip install fastadmin[django,pony]           # Django with Pony ORM
pip install fastadmin[flask,sqlalchemy]      # Flask with SQLAlchemy (includes greenlet)
""",
                },
                {
                    "type": "text",
                    "content": "Or install with Poetry:",
                },
                {
                    "type": "code-bash",
                    "content": """
poetry add 'fastadmin[fastapi,django]'
poetry add 'fastadmin[fastapi,tortoise-orm]'
poetry add 'fastadmin[fastapi,pony]'
poetry add 'fastadmin[fastapi,sqlalchemy]'
poetry add 'fastadmin[django]'
poetry add 'fastadmin[django,pony]'
poetry add 'fastadmin[flask,sqlalchemy]'
""",
                },
                {
                    "type": "alert-info",
                    "content": "When using SQLAlchemy, the <code>greenlet</code> package is required (included in the <code>fastadmin[sqlalchemy]</code> extra).",
                },
                {
                    "type": "text",
                    "content": "Configure the required settings with environment variables:",
                },
                {
                    "type": "alert-info",
                    "content": "You can add these variables to a <code>.env</code> file and load them with python-dotenv. See <a href='https://vsdudakov.github.io/fastadmin#settings'>all settings</a> in the full documentation.",
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
        # settings
        case "#settings":
            return [
                {
                    "type": "text",
                    "content": "The following settings have default values:",
                },
                {
                    "type": "alert-info",
                    "content": "Set environment variables or create a <code>.env</code> file and load it with the <code>python-dotenv</code> package.",
                },
                {"type": "code-python", "content": inspect.getsource(Settings)},
                {
                    "type": "alert-warning",
                    "content": "Settings without default values are required.",
                },
            ]
        # widgets
        case "#registering-widgets":
            return [
                {
                    "type": "text-lead",
                    "content": (
                        "To show dashboard widgets, define @widget_action methods on your model admin "
                        "and list their method names in the model admin's widget_actions attribute."
                    ),
                },
                {
                    "type": "alert-warning",
                    "content": (
                        "If you forget to add the method name to widget_actions, the widget will "
                        "not appear on the dashboard."
                    ),
                },
                {
                    "type": "code-python",
                    "content": """from fastadmin import TortoiseModelAdmin, widget_action
from fastadmin.models.schemas import (
    WidgetActionChartProps,
    WidgetActionInputSchema,
    WidgetActionResponseSchema,
    WidgetActionType,
)


class UserAdmin(TortoiseModelAdmin):
    # Register widgets by method name
    widget_actions = ("users_chart",)

    @widget_action(
        widget_action_type=WidgetActionType.ChartLine,
        widget_action_props=WidgetActionChartProps(x_field="x", y_field="y"),
        tab="Analytics",
        title="Users over time",
    )
    async def users_chart(self, payload: WidgetActionInputSchema) -> WidgetActionResponseSchema:
        # Build and return data for the chart
        return WidgetActionResponseSchema(
            data=[
                {"x": "2026-01-01", "y": 10},
                {"x": "2026-01-02", "y": 15},
            ],
        )
""",
                },
            ]
        case "#widget-methods-and-attributes":
            return [
                {
                    "type": "text",
                    "content": (
                        "Use the @widget_action decorator on ModelAdmin methods to declare "
                        "dashboard widgets and actions. The decorator attaches metadata used "
                        "to render chart widgets and action forms on the dashboard."
                    ),
                },
                {"type": "code-python", "content": inspect.getsource(widget_action)},
                {
                    "type": "text",
                    "content": (
                        "Widget actions use the following types for configuration "
                        "(chart props, arguments, filters and payload schema):"
                    ),
                },
                {
                    "type": "code-python",
                    "content": "\n\n".join(
                        [
                            inspect.getsource(WidgetActionChartProps),
                            inspect.getsource(WidgetActionArgumentProps),
                            inspect.getsource(WidgetActionProps),
                            inspect.getsource(WidgetActionFilter),
                            inspect.getsource(WidgetActionInputSchema),
                            inspect.getsource(WidgetActionResponseSchema),
                        ]
                    ),
                },
                {
                    "type": "alert-warning",
                    "content": (
                        "If you call @widget_action() without arguments, FastAdmin uses the "
                        "documented defaults: tab='Default', title='Action', "
                        "widget_action_type=WidgetActionType.Action and no props or filters."
                    ),
                },
                {
                    "type": "alert-info",
                    "content": (
                        "After defining a @widget_action method, add its name to the model admin's "
                        "<code>widget_actions</code> attribute so that it is rendered on the dashboard."
                    ),
                },
            ]
        case "#widget-chart-types":
            return [
                {
                    "type": "text",
                    "content": (
                        "The FastAdmin dashboard supports the following widget action types for charts and actions:"
                    ),
                },
                {"type": "code-python", "content": inspect.getsource(WidgetActionType)},
                {
                    "type": "alert-warning",
                    "content": (
                        "Chart-* widget actions render charts on the dashboard; the Action "
                        "type renders a simple action widget. See "
                        f"<a href='{ANTD_CHARTS_EXAMPLES}' target='_blank'>antd charts</a> "
                        "for more details (e.g. how they look)."
                    ),
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
                            "content": [
                                {
                                    "type": "code-python",
                                    "content": read_example("examples/fastapi_tortoiseorm/example.py"),
                                }
                            ],
                        },
                        {
                            "name": "Django ORM",
                            "id": "models_django_orm",
                            "content": [
                                {
                                    "type": "code-python",
                                    "content": read_example("examples/django_djangoorm/orm/models.py"),
                                }
                            ],
                        },
                        {
                            "name": "SQLAlchemy",
                            "id": "models_sql_alchemy",
                            "content": [
                                {
                                    "type": "code-python",
                                    "content": read_example("examples/fastapi_sqlalchemy/example.py"),
                                }
                            ],
                        },
                        {
                            "name": "Pony ORM",
                            "id": "models_pony_orm",
                            "content": [
                                {
                                    "type": "code-python",
                                    "content": read_example("examples/fastapi_ponyorm/example.py"),
                                }
                            ],
                        },
                    ],
                },
            ]
        case "#authentication":
            return [
                {
                    "type": "alert-info",
                    "content": "You must implement <code>authenticate</code> and <code>change_password</code> in the model admin for the User model. See the example above.",
                },
            ]
        case "#model-methods-and-attributes":
            return [
                {
                    "type": "text",
                    "content": "The following methods and attributes are available for model admins:",
                },
                {"type": "code-python", "content": inspect.getsource(BaseModelAdmin)},
                {
                    "type": "alert-info",
                    "content": "Use <code>self.request</code> and <code>self.user</code> in your admin methods (permissions, save hooks, actions) to access request-scoped context.",
                },
                {
                    "type": "code-python",
                    "content": """class EventAdmin(TortoiseModelAdmin):
    async def has_change_permission(self, user_id=None):
        # request/user are available for current request context
        if self.user and self.user.get("is_superuser"):
            return True
        return False

    async def save_model(self, id, payload):
        if self.request:
            payload["changed_from_ip"] = getattr(self.request, "client", None)
        return await super().save_model(id, payload)
""",
                },
                {
                    "type": "text",
                    "content": "Model-admin-specific methods and attributes:",
                },
                {"type": "code-python", "content": inspect.getsource(ModelAdmin)},
            ]
        case "#model-form-field-types":
            return [
                {
                    "type": "text",
                    "content": "The following form field types are available for model admins:",
                },
                {"type": "code-python", "content": inspect.getsource(WidgetType)},
                {
                    "type": "alert-warning",
                    "content": "See <a href='https://ant.design/components/overview' target='_blank'>antd components</a> for more details (e.g. how they look).",
                },
                {
                    "type": "text",
                    "content": "For file and image fields use <code>UploadFile</code> and <code>UploadImage</code> widgets in <code>formfield_overrides</code>. Implement <code>upload_file(obj, field_name, file_name, file_content)</code> on the model admin to handle uploads; it must return the file URL (e.g. after saving to disk or S3).",
                },
                {
                    "type": "text",
                    "content": "Use <code>formfield_overrides</code> to customize widget props per field. You can set <code>label</code> for a custom field label and <code>help</code> for description text below the field:",
                },
                {
                    "type": "code-python",
                    "content": """formfield_overrides = {
    "username": (
        WidgetType.SlugInput,
        {
            "required": True,
            "label": "Custom label",
            "help": "Detailed description of the field",
        },
    ),
}""",
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
                            "content": [
                                {
                                    "type": "code-python",
                                    "content": read_example("examples/fastapi_tortoiseorm/example.py"),
                                }
                            ],
                        },
                        {
                            "name": "Django ORM",
                            "id": "inlines_django_orm",
                            "content": [
                                {
                                    "type": "code-python",
                                    "content": read_example("examples/django_djangoorm/orm/models.py"),
                                }
                            ],
                        },
                        {
                            "name": "SQLAlchemy",
                            "id": "inlines_sql_alchemy",
                            "content": [
                                {
                                    "type": "code-python",
                                    "content": read_example("examples/fastapi_sqlalchemy/example.py"),
                                }
                            ],
                        },
                        {
                            "name": "Pony ORM",
                            "id": "inlines_pony_orm",
                            "content": [
                                {
                                    "type": "code-python",
                                    "content": read_example("examples/fastapi_ponyorm/example.py"),
                                }
                            ],
                        },
                    ],
                },
            ]
        case "#inline-methods-and-attributes":
            return [
                {
                    "type": "text",
                    "content": "The following methods and attributes are available for inline model admins:",
                },
                {
                    "type": "alert-info",
                    "content": "See the BaseModelAdmin methods and attributes in the model admin section.",
                },
                {
                    "type": "text",
                    "content": "Inline-model-specific methods and attributes:",
                },
                {"type": "code-python", "content": inspect.getsource(InlineModelAdmin)},
            ]
        # changelog
        case "#changelog":
            return [
                {
                    "type": "alert-info",
                    "content": "See what was added, changed, fixed, or improved in the latest versions.",
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
        "description": f"{NAME} is an easy-to-use admin dashboard for FastAPI, Django, and Flask, inspired by Django Admin.",
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
        fh.write(html_minify(index_html))

    readme_template = env.get_template("templates/readme.md")
    readme_md = readme_template.render(**context)
    with Path.open(Path(ROOT_DIR / ".." / "README.md"), "w") as fh:
        fh.write(readme_md)


if __name__ == "__main__":
    build()
