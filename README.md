# Market Mapper V1

A Manitoba vendor opportunity directory website — helping vendors discover farmers markets, craft fairs, food festivals, and other selling opportunities across Manitoba.

## Quick Start

```bash
# Create virtual environment
uv venv .venv --python python3.11
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt

# Copy environment file
cp .env.example .env  # then edit as needed

# Run migrations
python manage.py migrate

# Seed Manitoba regions
python manage.py seed_regions

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

## Project Structure

- `config/` — Django project settings (split into base/dev/prod)
- `apps/opportunities/` — Core opportunity listings
- `apps/pages/` — Static/marketing pages
- `apps/newsletter/` — Beehiiv newsletter integration (stub)
- `templates/` — Project-level templates
- `static/` — Static assets (CSS, JS, images)

## Tech Stack

- Django 5.1+
- SQLite (dev) / PostgreSQL (prod)
- WhiteNoise for static files
- django-filter for search/filtering
- django-environ for configuration

## Manitoba Regions

Winnipeg, Interlake, Pembina Valley, Central Plains, Westman, Parklands, Northern Manitoba, Eastman, Southeast
