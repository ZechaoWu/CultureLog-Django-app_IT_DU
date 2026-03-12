# CultureLogDjango Startup Guide

This package contains only the `CultureLogDjango` project.

## Requirements
- Python 3.10+
- pip

## Quick Start
1. Open terminal in project root:

```bash
cd CultureLogDjango
```

2. Create and activate virtual environment:

```bash
python -m venv .venv
```

Windows (PowerShell):

```bash
.venv\Scripts\Activate.ps1
```

Windows (CMD):

```bash
.venv\Scripts\activate.bat
```

macOS/Linux:

```bash
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Apply database migrations:

```bash
python manage.py migrate
```

5. Start development server:

```bash
python manage.py runserver
```

6. Open in browser:

```text
http://127.0.0.1:8000/
```

## Optional Checks

```bash
python manage.py check
python manage.py test core
```

## Notes
- If port 8000 is occupied, run: `python manage.py runserver 127.0.0.1:8001`
- You can register a new account from the Register page.
