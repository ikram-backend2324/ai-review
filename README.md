# QuizBot — Django Web App

AI-powered quiz web application built with Django + SQLite + Jazzmin admin.

## Features

- **Two roles**: regular User and Admin (Django Admin with Jazzmin UI)
- **AI-generated questions** via OpenRouter API (Mistral 7B)
- **Loading overlay** while AI responds
- **Session tracking**: scores, ratings, history
- **Beautiful dark UI**: glassmorphism, aurora gradients, smooth animations

## Quick Start

### 1. Clone / extract the project

```bash
cd quizbot
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Linux / Mac
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
# Edit .env and fill in:
#   DJANGO_SECRET_KEY  — generate with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
#   OPENROUTER_API_KEY — get from https://openrouter.ai
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Seed subjects

```bash
python manage.py seed_subjects
```

### 7. Create admin superuser

```bash
python manage.py createsuperuser
```

### 8. Run development server

```bash
python manage.py runserver
```

Open http://127.0.0.1:8000/ in your browser.

## Admin Panel

Visit http://127.0.0.1:8000/admin/ — powered by **Jazzmin** with a dark theme.

From the admin panel you can:
- Manage users and subjects
- View all quiz sessions with scores and ratings
- Browse individual answers with AI feedback

## Production (Gunicorn + WhiteNoise)

```bash
python manage.py collectstatic --noinput
gunicorn quizbot.wsgi:application --bind 0.0.0.0:8000
```

## Project Structure

```
quizbot/
├── quizbot/           # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── quiz/              # Main app
│   ├── models.py      # Subject, QuizSession, QuizAnswer
│   ├── views.py       # All views (auth + quiz + AJAX)
│   ├── admin.py       # Jazzmin-powered admin
│   ├── ai_service.py  # OpenRouter AI calls
│   ├── urls.py
│   ├── management/
│   │   └── commands/
│   │       └── seed_subjects.py
│   └── templates/quiz/
│       ├── login.html
│       ├── register.html
│       ├── home.html
│       ├── quiz.html
│       ├── results.html
│       └── history.html
├── templates/
│   └── base.html      # Shared layout with loading overlay
├── requirements.txt
├── .env.example
└── manage.py
```
