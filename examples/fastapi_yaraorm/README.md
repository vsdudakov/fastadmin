# FastAdmin — FastAPI + Yara ORM example

A minimal admin dashboard for a FastAPI app backed by
[Yara ORM](https://github.com/vsdudakov/yara-orm) (a fast, async, Tortoise-style
Python ORM with a Rust engine).

## Run

```bash
make install
make run
```

Then open <http://localhost:8090/admin> and sign in with `admin` / `admin`.

The example registers `User`, `Tournament`, `BaseEvent` and `Event` admins,
demonstrating foreign keys, one-to-one and many-to-many relations, an inline,
bulk actions, display fields, a dashboard chart widget and file uploads.

See the [FastAdmin documentation](https://vsdudakov.github.io/fastadmin/) for
details.
