# 🗺️ Market Mapper

**Manitoba's vendor opportunity database.**

Find farmers markets, craft fairs, festivals, exhibitions, flea markets, night markets, and more — all in one place. Built for vendors who want to know where to sell, what it costs, and when to apply.

🌐 **Live at:** [test.casamaccoy.ca](https://test.casamaccoy.ca) (staging) → [marketmapper.ca](https://marketmapper.ca) (coming soon)

---

## What It Does

- **Browse 39+ verified vendor opportunities** across Manitoba, searchable by region, type, and status
- **Honest confidence scoring** (1-5) — we don't guess, we verify
- **Vendor fee data** where available — from $20 flea market tables to $2,000 night market booths
- **Blog with real content** — seasonal guides, fee comparisons, rural market roundups
- **SEO category pages** — 90+ auto-generated landing pages for type × region combos
- **Map view** — Leaflet.js OpenStreetMap with clickable markers
- **Modern admin** — Django Unfold theme with branded sidebar, tabs, and dashboard stats

## Tech Stack

- **Backend:** Django 5.2, Python 3.11
- **Database:** PostgreSQL 15 (production) / SQLite (development)
- **Frontend:** Tailwind CSS (CDN), Leaflet.js
- **Server:** Nginx → Gunicorn → Django on Debian 12 LXC
- **SSL:** Cloudflare Tunnel (zero-config HTTPS)
- **Admin:** django-unfold with custom branding
- **Content:** Markdown rendering via `python-markdown`

## Project Structure

```
marketmapper/
├── apps/
│   ├── opportunities/   # Core: vendor markets, regions, badges
│   ├── blog/            # Blog posts with Markdown + featured images
│   ├── stories/         # Vendor success stories
│   ├── newsletter/      # Newsletter signup
│   └── pages/           # Static pages (home, about, contact, privacy)
├── config/
│   ├── settings/
│   │   ├── base.py      # Shared settings + Unfold config
│   │   └── production.py # PostgreSQL, security headers, HTTPS
│   ├── urls.py
│   └── wsgi.py
├── deploy/
│   └── gunicorn.conf.py
├── static/              # Source static files (CSS, images, logo)
├── templates/           # Django templates (Tailwind-styled)
├── manage.py
└── requirements.txt
```

## Quick Start (Development)

```bash
# Clone
git clone https://github.com/dArk-EThos/marketmapper.git
cd marketmapper

# Set up Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your SECRET_KEY

# Run migrations (SQLite for dev)
python manage.py migrate

# Create a superuser
python manage.py createsuperuser

# Seed regions
python manage.py shell -c "
from apps.opportunities.models import Region
regions = ['Winnipeg', 'Pembina Valley', 'Central Plains', 'Parklands',
           'Interlake', 'Eastman', 'Northern Manitoba', 'Westman', 'Southeast']
for name in regions:
    Region.objects.get_or_create(name=name)
print(f'Seeded {Region.objects.count()} regions')
"

# Run the dev server
python manage.py runserver
```

Visit http://localhost:8000 and http://localhost:8000/admin/

## Production Deployment

See `deploy/` directory for Gunicorn and systemd configs. The production stack runs:

- **Debian 12 LXC** on Proxmox
- **Nginx** reverse proxy (port 80, hardcoded `X-Forwarded-Proto: https`)
- **Gunicorn** with 3 workers + gthread
- **PostgreSQL 15**
- **Cloudflare Tunnel** for zero-config HTTPS
- **WhiteNoise** for static file serving

## Regions Covered

| Region | Markets |
|--------|---------|
| Winnipeg | 15 |
| Pembina Valley | 7 |
| Interlake | 5 |
| Central Plains | 3 |
| Westman | 3 |
| Northern Manitoba | 2 |
| Parklands | 2 |
| Southeast | 2 |

## License

Private project. All rights reserved.

## Contact

Built by Howie. Questions? [Contact us](https://test.casamaccoy.ca/contact/).
