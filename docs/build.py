from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import date


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


def get_context():
    return {
        "versions": get_versions(),
        "created_date": "7 March 2023",
        "updated_date": date.today().strftime("%d %B %Y"),
    }


def build():
    env = Environment(
        loader=FileSystemLoader("."),
        autoescape=select_autoescape()
    )
    template = env.get_template("index.tmpl.html")
    context = get_context()
    output = template.render(**context)

    with open("index.html", "w") as fh:
        fh.write(output)


if __name__ == "__main__":
    build()
