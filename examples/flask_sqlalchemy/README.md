## Flask + SQLAlchemy 2.x Example

- Uses an in-memory SQLite instance (async engine with aiosqlite)
- Creates a superuser with username/password `admin`/`admin` on startup
- Environment variables are set in `__init__.py` and `example.py`

```bash
make install  # Create virtualenv with Poetry
make run      # Run init_db + create_superuser, then start Flask on port 8090
```

Then open <http://127.0.0.1:8090/admin/> and have fun.

Reference: see `examples/fastapi_sqlalchemy` for the FastAPI version of this example.
