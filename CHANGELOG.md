# Changelog

All notable changes to FastAdmin are documented in this file.

## 0.5.0

- Restructure the project tooling: PEP 621 `pyproject.toml` with the `uv_build` backend and a committed `uv.lock` (poetry removed).
- Replace black/isort/mypy with `ruff check`, `ruff format` and `ty`.
- Replace the custom HTML documentation with an MkDocs Material site deployed to GitHub Pages: <https://vsdudakov.github.io/fastadmin/>.
- Add a root `CHANGELOG.md`; rename `LICENSE` to `LICENSE.md`; rewrite `README.md`.
- Rework GitHub workflows: split CI (lint, backend test matrix, frontend, per-extras install checks) and add docs deploy and tag-driven PyPI release workflows.
- Upgrade all backend and frontend dependencies (latest minors; antd 6.5, eslint 10.6, vitest 4.1).
- No changes to the public FastAdmin API.

## 0.4.9

- Add `obj` parameter to `upload_file` method.
- Add `get_file_url` method to model admin.

## 0.4.8

- Add toolbar actions to widget action results.
- Add table view to widget action results.
- Add JSON view to widget action results.
- Enhance documentation for the `upload_file` method.
- Add `str` type for pk.

## 0.4.7

- Add `sub_tab` to widget action props.
- Dark mode support.

## 0.4.6

- Add `max_height` to widget action props.
- Add highlight search results to widget action results.
- Add copy to clipboard to widget action results.
- Add expand results modal to widget action results.
- Add `menu_section` to model admins.

## 0.4.5

- Add `parent` argument to widget action props.
- Add wraps to decorator to keep the original function name and docstring.
- Add `pre_generate_models_schema` method to ModelAdmin to pre-generate models schema.
- Fix examples.

## 0.4.4

- Replace helmet to update title and description.
- Improve frontend coverage.

## 0.4.3

- Add `series` field to widget action props. Fix examples.
- Add search by actions.

## 0.4.2

- Replace `DashboardWidgetAdmin` with `widget_action` decorator (no backward compatibility).
- Fix mobile view.

## 0.4.1

- Fix upload file functionality. Fix examples.

## 0.4.0

- Add new upload file functionality (without backward compatibility). See documentation for details.
- Add example for Flask with SQLAlchemy.
- Removed `ADMIN_DISABLE_CROP_IMAGE` setting. Use `disableCropImage` prop in UploadImage widget instead.

## 0.3.11

- Fix API service errors.

## 0.3.10

- Fix file download issue for actions.

## 0.3.9

- Add response types for actions.
- Fix Decimal fields handling.

## 0.3.8

- Fix inline add/change issue.
- Fix inline filter reset issue.

## 0.3.7

- Fix filter reset issue.
- Fix date/time handling in transform helpers.
- Fix examples.
- Fix JSON textarea handling.

## 0.3.6

- Fix datetime/time handling in transform helpers.
- Revert `get_orm_list` method to original implementation. We can use `list_select_related` and `search_fields` for `prefetch_related_fields` and `additional_search_fields`.

## 0.3.5

- Enhance `get_orm_list` method to support `prefetch_related_fields` and `additional_search_fields`.
- Add request/user context on `BaseModelAdmin` for per-request custom logic.

## 0.3.4

- Fix sort by and search by relations. Fix examples.

## 0.3.3

- Fix `DetachedInstanceError` when session is closed after commit.
- Fix list display widths.
- Fix Flask issues.

## 0.3.2

- Add `formfield_overrides` example. Add `label` and `help` props.

## 0.3.1

- Fix SQLAlchemy required fields. Fix CI.

## 0.3.0

- Clean up documentation. Update dependencies. Fix linters and tests. Frontend refactoring.

## 0.2.22

- Fix upload base64 widget; add `disableCropImage` prop. Fix examples.

## 0.2.21

- Fix cleaning of async select fields on forms.

## 0.2.20

- Fix `_id` fields handling. Bump backend and frontend packages.

## 0.2.19

- Fix `is_pk` for Tortoise ORM.

## 0.2.18

- Fix M2M/FK handling for SQLAlchemy with PostgreSQL (convert str to int).

## 0.2.17

- Fix FK handling for SQLAlchemy with PostgreSQL (convert str to int).

## 0.2.16

- Add `ADMIN_DISABLE_CROP_IMAGE` setting to configure image cropping on upload.

## 0.2.15

- Fix password logic for user model.

## 0.2.14

- Make permission functions awaitable. Bump frontend and backend packages.

## 0.2.13

- Fix edit page frontend issue for Date field.

## 0.2.12

- Remove python-dotenv dependency. Bump Django. Add Django example.

## 0.2.11

- Fix examples. Fix Pony ORM (delete, update M2M). Allow sorting by custom columns. Fix `list_display` ordering.

## 0.2.10

- Fix empty M2M issue. Optimize unit tests. Fix Pony ORM. Optimize Tortoise ORM search.

## 0.2.9

- Fix modal inline dialogs. Fix M2M multiple select.

## 0.2.8

- Fix SQLAlchemy delete functionality. Add more examples.

## 0.2.7

- Fix helper functions. Add regex support.

## 0.2.6

- Add edit button for async select.

## 0.2.5

- Fix async select in inlines.

## 0.2.4

- Fix dashboard widgets and auto-register inlines.

## 0.2.3

- Fix filter issue on list views. Remove Jinja from dependencies.

## 0.2.2

- Fix datetime-related bugs.

## 0.2.1

- Update packages. Fix linters and tests in Vite frontend. Remove Pydantic from dependencies.

## 0.2.0

- Update packages. Use Vite instead of deprecated react-scripts.
