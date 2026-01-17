# JEE Predictor

A Django web application that predicts JEE college cutoffs based on student ranks and categories.

## Features
- College cutoff prediction
- Responsive UI
- Railway deployment ready

## Tech Stack
- Django 4.2.7
- SQLite (local) / MySQL (production)
- WhiteNoise for static files
- Bootstrap (assumed)

## Local Setup
1. Clone repo: `git clone https://github.com/YOUR_USERNAME/jee_predictor.git`
2. Create venv: `python -m venv venv`
3. Activate venv & install: `pip install -r requirements.txt`
4. Run migrations: `python manage.py migrate`
5. Start server: `python manage.py runserver`

## Production
Set `DATABASE_URL` env var for Railway deployment.
