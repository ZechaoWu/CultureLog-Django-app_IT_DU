
````markdown
# CultureLog

A Django web application for tracking books and movies, managing personal entries, and writing reviews.

## Overview

CultureLog is a web application developed for the Internet Technology coursework. It allows users to register and log in, browse and manage media items, submit reviews, search and filter content, and maintain a personalised media tracking experience.

The project is built with Django on the backend and uses HTML, CSS, and JavaScript on the frontend. It includes database interaction, user authentication, and interactive features required by the coursework specification.

## Main Features

- User registration, login, and logout
- Access-controlled user actions
- Add, edit, browse, and delete media items
- Submit, edit, and display reviews
- Search and filter media content
- Profile-related functionality
- Django-based server-rendered interface with client-side interactivity
- Responsive UI for common screen sizes

## Tech Stack

- **Backend:** Python, Django
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQLite (development)
- **Testing:** Django test framework
- **Version Control:** Git + GitHub

## Links

- **Repository:** https://github.com/ZechaoWu/CultureLog-Django-app_IT_DU
- **Deployed Application:https://culturelog-django-app-it-du.onrender.com

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/ZechaoWu/CultureLog-Django-app_IT_DU.git
cd CultureLog-Django-app_IT_DU
````

### 2. Create and activate a virtual environment

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` in the project root, then update the values as needed.

Example:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 5. Apply database migrations

```bash
python manage.py migrate
```

### 6. Create a superuser (optional)

```bash
python manage.py createsuperuser
```

### 7. Run the development server

```bash
python manage.py runserver
```

Then open:

```text
http://127.0.0.1:8000/
```

## Running Tests

To run all tests:

```bash
python manage.py test
```

To run tests for the main app only:

```bash
python manage.py test core
```

## Project Structure

```text
CultureLog-Django-app_IT_DU/
├── config/              # Django project configuration
├── core/                # Main app: models, views, forms, tests, URLs
├── docs/                # Supporting project documentation
├── templates/           # HTML templates
├── manage.py
├── requirements.txt
├── README.md
└── STARTUP_GUIDE.md
```

## Production Deployment Notes

Before deployment:

* Set `DEBUG=False`
* Configure `ALLOWED_HOSTS`
* Use environment variables for secrets
* Configure static file handling correctly
* Run `python manage.py collectstatic`
* Use a production-ready database if required by the hosting platform

## Coursework Context

This project was developed as part of the **Internet Technology (M)** coursework on web application implementation.

It aims to demonstrate:

* user authentication
* database interaction
* user input handling
* frontend interactivity
* responsive design
* testing
* accessibility and sustainability considerations

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

## Authors

Zechao Wu
Cheng Li
Luyi Yuan

````


