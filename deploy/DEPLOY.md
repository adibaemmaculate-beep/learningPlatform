# Deploying on Ubuntu: Gunicorn + Nginx + Tailscale Funnel

This serves the platform publicly over HTTPS without router port-forwarding.
Traffic path:

```
Internet ──HTTPS──▶ Tailscale Funnel (443, auto TLS)
                        │  http://127.0.0.1:8080
                        ▼
                     Nginx (static/uploads + reverse proxy)
                        │  http://127.0.0.1:8000
                        ▼
                     Gunicorn ──▶ Django (config.settings.production)
```

All commands run **on the Ubuntu server**. Paths below assume the repo is at
`/home/sean/learningPlatform` and the Linux user is `sean` — adjust if different.

---

## 1. System packages

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip nginx
```

> Node/`npm` are NOT required: the compiled `static/css/main.css` is committed.
> Only install Node if you need to rebuild Tailwind (`npm install && npm run build:css`).

## 2. App setup

```bash
cd /home/sean/learningPlatform
git pull

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Environment — see section 3 before running migrate
python manage.py migrate --settings=config.settings.production
python manage.py collectstatic --noinput --settings=config.settings.production
python manage.py seed_admin --settings=config.settings.production
```

## 3. Configure `.env`

Find your public Funnel hostname:

```bash
tailscale status --json | grep -i dnsname | head -1    # -> <machine>.<tailnet>.ts.net
```

Then set these in `.env` (production settings read it):

```ini
DEBUG=False
SECRET_KEY=<a long random string>          # python -c "import secrets;print(secrets.token_urlsafe(50))"

# Use the Funnel hostname (no scheme here)
ALLOWED_HOSTS=<machine>.<tailnet>.ts.net,localhost,127.0.0.1

# CSRF — MUST include the scheme. Without this, login/admin POSTs return 403.
CSRF_TRUSTED_ORIGINS=https://<machine>.<tailnet>.ts.net

# Database: leave DB_ENGINE unset to use SQLite (default).
# To use PostgreSQL instead, set DB_ENGINE=postgresql plus the DB_* vars.
```

> `production.py` sets `SECURE_SSL_REDIRECT=True` and trusts `X-Forwarded-Proto`,
> which Nginx/Funnel supply — so there's no redirect loop. If you ever run without
> the proxy and hit a loop, set `SECURE_SSL_REDIRECT=False` in `.env`.

## 4. Gunicorn service (systemd)

Gunicorn listens on a local TCP port (`127.0.0.1:8000`). Edit
`deploy/gunicorn.service` if your user/paths differ, then:

```bash
sudo cp deploy/gunicorn.service /etc/systemd/system/learningplatform.service
sudo systemctl daemon-reload
sudo systemctl enable --now learningplatform
sudo systemctl status learningplatform --no-pager     # should be "active (running)"
```

## 5. Nginx

```bash
sudo cp deploy/nginx.conf /etc/nginx/sites-available/learningplatform
sudo ln -sf /etc/nginx/sites-available/learningplatform /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
# Let nginx (www-data) traverse into the home dir to read static/uploads:
sudo chmod o+x /home/sean
sudo nginx -t
sudo systemctl restart nginx          # restart (not reload) when adding a new listen port
```

Quick local check (still on the server):

```bash
curl -I -H "X-Forwarded-Proto: https" http://127.0.0.1:8080/
# Expect HTTP/1.1 200 or 302 (login) — NOT a redirect loop or 502.
```

## 6. Expose it with Tailscale Funnel

Funnel must be enabled for your tailnet (Admin console → Funnel; allow the
`funnel` node attribute in ACLs). Then:

```bash
sudo tailscale funnel --bg 8080      # public HTTPS (443) -> local Nginx on 8080
tailscale funnel status              # shows the public https URL
```

Visit `https://<machine>.<tailnet>.ts.net/` from anywhere.

To stop exposing publicly: `sudo tailscale funnel --https=443 off`
(Use `tailscale serve` instead of `funnel` for tailnet-only, private access.)

> Running a second app on the same machine? Funnel also supports ports 8443 and
> 10000: `sudo tailscale funnel --bg --https=8443 <other_local_port>`. Each app
> must listen on its OWN local port — two Nginx server blocks on the same port
> with `server_name _` collide, and the alphabetically-first site wins.

---

## Updating after code changes

```bash
cd /home/sean/learningPlatform
git pull
source venv/bin/activate
pip install -r requirements.txt          # if requirements changed
python manage.py migrate --settings=config.settings.production
python manage.py collectstatic --noinput --settings=config.settings.production
sudo systemctl restart learningplatform
```

## Troubleshooting

| Symptom                                      | Fix                                                                                                                                                    |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `502 Bad Gateway`                            | Gunicorn down: `sudo systemctl status learningplatform`, `journalctl -u learningplatform -e`                                                           |
| Infinite redirect / `ERR_TOO_MANY_REDIRECTS` | `X-Forwarded-Proto` not reaching Django — confirm Nginx `proxy_set_header X-Forwarded-Proto https;` and `SECURE_PROXY_SSL_HEADER` in production.py     |
| `403 CSRF` on login/admin                    | Add `https://<host>` to `CSRF_TRUSTED_ORIGINS` in `.env`, restart service                                                                              |
| `DisallowedHost`                             | Add the Funnel hostname to `ALLOWED_HOSTS`                                                                                                             |
| New `listen` port not bound after `reload`   | Use `sudo systemctl restart nginx` — a SIGHUP reload won't always open a brand-new listen socket                                                       |
| CSS missing / unstyled                       | `collectstatic` then check Nginx `/static/` alias path and `sudo chmod o+x /home/<user>`                                                               |
| Browser shows an old/previous app at the URL | A cached **service worker** from the previous app — unregister it at `chrome://serviceworker-internals/` and clear site data; the server is unaffected |
