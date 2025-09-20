# Procfile pour le déploiement sur Render et autres plateformes

# Service web principal
web: gunicorn silence_dor.wsgi:application --bind 0.0.0.0:$PORT --settings=silence_dor.settings_production

# Worker Celery (optionnel)
worker: celery -A silence_dor worker --loglevel=info

# Beat Celery (optionnel)
beat: celery -A silence_dor beat --loglevel=info