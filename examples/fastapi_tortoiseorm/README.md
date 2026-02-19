## FastAPI + Tortoise ORM Example

- Uses an in-memory SQLite instance
- Creates a superuser with username/password `admin`/`admin`
- Environment variables are set in `__init__.py`

```bash
make install  # Create virtualenv with Poetry
make run      # Start the FastAPI dev server
```

Then open <http://127.0.0.1:8090/admin/> and have fun.