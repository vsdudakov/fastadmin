# Changelog

All notable changes to FastAdmin are documented in this file.

## 0.10.0

### Features

- **Form field labels**: `list_display_labels` now also applies to add/change
  form fields (and inline forms), not only list-page column headers. An
  explicit `label` in `formfield_overrides` widget props still wins.
- **Localization**: the admin UI is fully translatable. Bundled languages:
  English, Russian, German, Spanish, French and Chinese. New `ADMIN_LANGUAGE`
  setting selects the default language (`en` by default; set to empty to
  auto-detect from the browser). Users can switch the language from the header
  settings menu; the choice is persisted in the browser and also switches the
  Ant Design and dayjs locales (dates, pagination, pickers).
- **Theme modes**: the header settings menu now offers Light, Dark and System
  themes. System (the default) follows the OS appearance live via
  `prefers-color-scheme`.

### Frontend

- **Apple-like design polish**: transparent macOS-style sidebar, frosted-glass
  dropdowns/popovers/pickers, blurred modal backdrop, overlay scrollbars,
  accent-tinted text selection, subtle table row hover and refined button
  radii. The configured `primary_color` remains the accent everywhere.
- **antd deprecations fixed**: `Collapse expandIconPosition` →
  `expandIconPlacement`, `Transfer listStyle` → `styles.section`,
  `Descriptions.Item` JSX children / `contentStyle` → the `items` API with
  `styles.content`.
- **i18next is now registered via `initReactI18next`** so components resolve
  translations (with interpolation) even outside an explicit
  `I18nextProvider`.

## 0.9.1

### Security

- **Passwords**: saving a user from the change form no longer destroys the
  password by re-hashing the stored hash. The change form displayed the current
  hash in the read-only password field and echoed it back on Save, and the
  save hook hashed it again. The frontend now excludes `PasswordInput` fields
  from the change payload, and the backend additionally drops a submitted
  password value that matches the stored one, so third-party clients that echo
  the hash are also safe. Passwords are changed only via the change-password
  endpoint / modal.

## 0.9.0

### Features

- **Column labels**: new `list_display_labels` ModelAdmin attribute
  (`{"field": "Header"}`) overrides or translates auto-generated list-page
  column titles. Sorting, filtering and data binding stay keyed by the field
  name.
- **Actions without selection**: `@action(requires_selection=False)` enables
  the Apply button without selecting rows; the action receives an empty `ids`
  list and should treat it as "all objects".

### Frontend

- **Apple-like design refresh**: frosted-glass sticky header with hairline
  borders (the configured `primary_color` now serves as the accent instead of
  the header background), larger continuous corner radii, softer diffuse
  shadows, `#f5f5f7`/`#161617` layout backgrounds, tighter letter spacing and
  transparent table headers. The rich-text editor accent follows
  `primary_color` instead of a hardcoded teal.
- **Dependencies**: antd 6.5.1, i18next 26, react-i18next 17, vite 8, jsdom 29,
  TypeScript 6.0, vitest 4.1.10, eslint 10.7; `quill-delta` added to satisfy a
  peer dependency and `baseUrl` removed from `tsconfig.json` (deprecated in
  TypeScript 6).

## 0.8.3

Correctness and security fixes from a full-codebase review. The only public API
addition is the backward-compatible `has_action_permission` model-admin hook.

### Security

- **Actions**: the `action` endpoint now enforces permissions server-side via a
  new `has_action_permission` hook (defaults to `has_change_permission`), so a
  read-only admin can no longer run a registered bulk action. Override the hook
  to allow a read-only user to run a specific non-mutating action.
- **Passwords**: editing a user with an empty password field no longer
  overwrites the stored hash with a hash of the empty string.
- **JWT**: signing and verifying are refused when `ADMIN_SECRET_KEY` is unset or
  empty, closing an empty-secret token-forgery path and returning a clear
  configuration error instead of an HTTP 500.

### Backend

- **All ORMs**: a legitimate primary key / user id of `0` no longer misroutes a
  save (update vs insert) or is rejected as unauthenticated.
- **SQLAlchemy**: `get_model_pk_name` resolves non-autoincrement primary keys
  (UUID/string) instead of falling back to `"id"`; `contains`/`icontains`
  filters cast to text so they work on integer columns; the primary key is
  excluded from `required`; and the generated primary key is read before commit
  so create/update is safe under the default `expire_on_commit=True`.
- **Tortoise / Django / Yara**: a falsy database default (`0`/`False`/`""`) no
  longer marks a field as required, and the primary key is excluded from
  `required`. Tortoise enum options now emit the scalar value, and Django choice
  options no longer swap the stored value with the human-readable label.
- **Serialization**: a field listed in both `exclude` and `list_display` now
  stays excluded from API responses.
- **Validation**: malformed date/datetime values, empty-condition filters
  (`field__`), unsupported or null export formats, and malformed request bodies
  on the Django integration now return HTTP 422 instead of an unhandled 500.
- **Settings**: `ADMIN_QUERY_MAX_LIMIT` and `ADMIN_SESSION_EXPIRED_AT` fall back
  to their defaults on a blank or non-numeric value instead of crashing the
  package at import.

## 0.8.2

Bug-fix follow-up to the 0.8.1 audit. No public API changes.

- **SQLAlchemy**: relationship (m2m) filter values are coerced to `int` for
  integer primary keys (previously raised HTTP 500 on strictly typed drivers
  such as PostgreSQL/asyncpg), and unsupported lookups on relation fields
  (e.g. `icontains`) are rejected with HTTP 422 instead of silently matching
  by primary-key equality.
- **Pony ORM**: the foreign-key filter rewrite no longer corrupts filters on
  plain columns whose name merely ends with `_id`, and list-view search now
  runs as a single OR'd WHERE clause instead of materializing every matching
  row once per search field.
- **Flask**: `HTTPException`s with an attached response (`abort(Response(...))`)
  are passed through unchanged, error headers (`Allow`, `WWW-Authenticate`,
  `Retry-After`, ...) are preserved on JSON error responses, and unhandled
  errors are logged with their traceback.
- **Filtering**: `IS NULL` is expressible again on text columns via
  `field__exact=null` (substring lookups keep the literal string `"null"`).
- **Frontend**: stop corrupting text fields whose content is the literal word
  `"true"`/`"false"` on the change form (booleans are now only coerced for
  boolean widgets), stop shape-based date detection for fields known to have
  no date widget, and pass the model configuration directly to
  `transformDataFromServer` so every call site gets the safe behavior.

## 0.8.1

Bug-fix release from a full-source audit of `main`. No public API changes.

- **Pony ORM**: fix list-view search crashing (HTTP 500) for models whose
  primary key is not named `id`, and fix multi-field ordering with mixed
  ascending/descending fields silently sorting by the wrong priority.
- **SQLAlchemy**: filtering a list by a many-to-many (or other relationship)
  field no longer raises an unhandled 500; it now matches on the related row's
  primary key.
- **Flask**: unhandled server errors now return a proper HTTP 500 with a generic
  message (previously sent as HTTP 200 and leaked the exception text), and API
  errors are returned as JSON `{"detail": ...}` matching the Django/FastAPI
  integrations instead of HTML error pages.
- **Filtering**: the literal strings `"true"`, `"false"`, and `"null"` are no
  longer coerced to `bool`/`None` on text fields, so a text column can be
  filtered for those exact values.
- **Frontend**: fix a form-save crash when a JSON field value is an object with a
  `date` key; stop corrupting text fields whose content looks like a date/time;
  render stored `CheckboxGroup` selections correctly; surface errors from
  dashboard action run/refresh; and use the react-query v5 `invalidateQueries`
  signature to avoid over-invalidating unrelated queries.
- Correct the `sortable_by` docstring to match actual behavior.

## 0.8.0

- Add a `register_encoder(type_, encoder)` hook to control how a type is
  serialized in every admin API response (e.g. a custom datetime format, an
  `Enum`'s label, or a domain value object). Custom encoders take precedence over
  the built-in `datetime`/`UUID`/`Decimal` handling (#136).

## 0.7.0

- Add support for [Yara ORM](https://github.com/vsdudakov/yara-orm) — a fast,
  async Python ORM with a Rust engine. New `YaraOrmModelAdmin` /
  `YaraOrmInlineModelAdmin` admin classes and a `fastadmin[yara-orm]` extra, with
  a runnable FastAPI example (`examples/fastapi_yaraorm`).
- Add a refresh button to the widget action results (toolbar and expand modal)
  so results can be re-run in place without losing scroll position (#132).

## 0.6.0

Security hardening release. No changes to the documented public API, but
several defaults are now stricter — review the notes below before upgrading.

- **Server-side permission enforcement**: `add`/`change`/`delete`/`export` now
  enforce the matching `has_*_permission` hook (previously UI-only), and
  `change_password` requires `has_change_permission` to change another user's
  password (fixes an account-takeover path).
- **Mass-assignment protection**: form saves only write fields allowed by
  `fields`/`exclude`/`readonly_fields`, so a crafted payload can no longer set
  hidden or read-only columns (e.g. `is_superuser`). Passwords are hashed via
  `change_password` on edit as well as create.
- **Injection fixes**: Pony ORM filters/search are parameterized (were built
  from f-strings); SQLAlchemy ordering uses column expressions instead of raw
  `text()`, and LIKE/ILIKE wildcards in filter/search values are escaped.
- **Filter allowlist & lookups**: filters are validated against `list_filter`
  (when set) and restricted to a fixed set of lookups, blocking relation-
  spanning/regex oracles over hidden columns.
- **CSV export injection**: exported cells starting with `=`, `+`, `-` or `@`
  are neutralized; CSV and JSON exports now emit the same columns.
- **Cookies & DoS**: the session cookie is now `Secure` + `SameSite=Lax` by
  default (configurable), list/export `limit` is capped by
  `ADMIN_QUERY_MAX_LIMIT`, and internal error details are no longer returned to
  clients.
- **New settings**: `ADMIN_SESSION_COOKIE_SECURE`, `ADMIN_SESSION_COOKIE_SAMESITE`,
  `ADMIN_QUERY_MAX_LIMIT`. `ADMIN_SESSION_EXPIRED_AT` is now coerced to `int`.
- **Frontend**: file/image upload links and `view_on_site` reject
  `javascript:`/`data:` URIs.

Upgrade note: for local HTTP development set `ADMIN_SESSION_COOKIE_SECURE=false`,
and set `list_filter`/`fields` where you relied on filtering arbitrary columns.

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
