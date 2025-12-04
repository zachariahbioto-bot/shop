# shop (Django)

This repository contains a minimal Django project created for local development.

Quick start

1. Create the virtual environment (already created in this setup):

```bash
python3 -m venv .venv
```

2. Activate and install dependencies:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

3. Run migrations and start the development server:

```bash
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver
```

Access the site at `http://127.0.0.1:8000/`.

Notes
- This setup is for local development only. Do not use `DEBUG=True` or the development `SECRET_KEY` in production.
