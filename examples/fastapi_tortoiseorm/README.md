## FastAPI + Tortoise ORM Example

- Uses in-memory SQLite 3 instance
- Creates "admin/admin" superuser
- Setup env variables in __init__.py

```bash
make install  # Creates virtualenv with Poetry
make run      # Runs fastapi dev
```

So open `http://127.0.0.1:8090/admin/` and have a fun!