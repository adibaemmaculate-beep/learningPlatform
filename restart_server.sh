#!/usr/bin/env bash
# Pull latest code and redeploy: rebuild assets, migrate, collect static,
# restart Gunicorn and reload Nginx. Run this on the server after pushing.
set -euo pipefail

cd "$(dirname "$0")"

echo "==> Pulling latest code"
git pull

echo "==> Activating virtualenv"
source venv/bin/activate

export DJANGO_SETTINGS_MODULE=config.settings.production

echo "==> Installing Python dependencies"
pip install -r requirements.txt

echo "==> Building CSS"
npm run build:css

echo "==> Applying migrations"
python manage.py migrate --noinput

echo "==> Collecting static files"
python manage.py collectstatic --noinput

echo "==> Restarting Gunicorn"
sudo systemctl restart learningplatform

echo "==> Reloading Nginx"
sudo systemctl reload nginx

echo "==> Done. Service status:"
sudo systemctl --no-pager --lines=0 status learningplatform nginx
