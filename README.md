# Shamva Innovators — AI & Coding Learning Platform

Django backend with HTML, Tailwind CSS, and JavaScript frontend.

## Quick start

```bash
cd learningPlatform
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
npm install
npm run build:css
python manage.py migrate
python manage.py seed_admin
python manage.py runserver
```

Open http://127.0.0.1:8000/

### Default admin credentials

- **Email:** `admin@example.com`
- **Password:** `changeme123`

### CSS build

Tailwind is compiled locally (not CDN). After changing templates or `static/src/input.css`:

```bash
npm run build:css
# or watch during development:
npm run watch:css
```

## Stage 5 — Projects, Announcements & Notifications

### New features

| Area | URLs / behavior |
|------|-----------------|
| **Student project** | `/student/project/` — create/edit capstone, publish to public page |
| **Student announcements** | Banner on all portal pages; `/student/announcements/` list |
| **Teacher announcements** | `/teacher/announcements/` — post, view read receipts |
| **Teacher projects** | `/teacher/projects/` — browse all student projects |
| **Public showcases** | `/students/` — published projects; `/students/<id>/` — full profile |
| **Email notifications** | Assignment published, submission received, grades released, announcements, account approved/rejected (console in dev unless SMTP configured) |

### Stage 5 test flow

1. **Teacher** → Announcements → Post (try "Students only" visibility)
2. **Student** → see banner on dashboard → open announcement (marks as read)
3. **Student** → My Project → fill details, upload images, check **Publish**
4. Visit **/students/** → click student card → verify public project page
5. **Teacher** → Projects → view student project
6. Toggle **email notifications** off in Settings → trigger an announcement → confirm no console email for that user

## Public deployment (Cloudflare Tunnel)

Use this when the Ubuntu server has **no public IP** (e.g. reachable only via
Tailscale / behind NAT/CGNAT) but you want a **custom domain** (bought on
Namecheap) accessible from anywhere. Cloudflare Tunnel terminates TLS and routes
public traffic to the server over an outbound-only connection — no open ports.

```
Internet → Cloudflare edge (TLS, your domain)
         → cloudflared (outbound tunnel, on the server)
         → Nginx (127.0.0.1:8080)  # serves /static/ and /uploads/
         → Gunicorn (127.0.0.1:8000)
         → Django (config.settings.production)
```

> Keep Nginx in front: WhiteNoise serves static files but **not** media uploads
> (`/uploads/`), which Nginx handles. Files: `deploy/nginx.conf`,
> `deploy/gunicorn.service`, `deploy/cloudflared-config.yml`.

### 1. Domain + DNS

1. Buy the domain on Namecheap.
2. Create a free Cloudflare account → **Add a site** → enter your domain.
3. In Namecheap (**Domain List → Manage → Nameservers → Custom DNS**), replace
   the nameservers with the two Cloudflare gives you. (Domain stays registered at
   Namecheap; only DNS moves to Cloudflare.) Wait for propagation.
4. In Cloudflare **SSL/TLS**, set encryption mode to **Flexible** (simplest; the
   tunnel itself is encrypted).

### 2. App on the server

```bash
cd /home/sean
git clone <your-repo-url> learningPlatform && cd learningPlatform
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
npm install && npm run build:css
export DJANGO_SETTINGS_MODULE=config.settings.production
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py seed_admin
```

> The repo's `.env` is committed and already production-ready (`DEBUG=False`,
> `ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS` set to `shamvainnovators.org`,
> `SECURE_SSL_REDIRECT=True`, SQLite). **Keep this repository PRIVATE** — `.env`
> contains the live `SECRET_KEY` and Gmail app password.
>
> SQLite note: `db.sqlite3` is git-ignored, so a fresh `migrate` starts with an
> empty database. To carry over existing data, copy your local `db.sqlite3` to the
> server (e.g. `scp db.sqlite3 sean@<tailscale-ip>:~/learningPlatform/`).

### 3. Gunicorn + Nginx (systemd)

Edit `deploy/gunicorn.service` (User/Group/paths) and `deploy/nginx.conf`
(the `/static/` and `/uploads/` alias paths), then:

```bash
sudo cp deploy/gunicorn.service /etc/systemd/system/learningplatform.service
sudo systemctl daemon-reload && sudo systemctl enable --now learningplatform

sudo cp deploy/nginx.conf /etc/nginx/sites-available/learningplatform
sudo ln -s /etc/nginx/sites-available/learningplatform /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### 4. Cloudflare Tunnel

```bash
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -o cloudflared.deb
sudo dpkg -i cloudflared.deb
cloudflared tunnel login                      # authorize your domain
cloudflared tunnel create learningplatform    # note the TUNNEL_ID it prints
```

Copy `deploy/cloudflared-config.yml` to `~/.cloudflared/config.yml`, fill in
`TUNNEL_ID` and the credentials path (hostnames are already set to
`shamvainnovators.org`). Then:

```bash
cloudflared tunnel route dns learningplatform shamvainnovators.org
cloudflared tunnel route dns learningplatform www.shamvainnovators.org
sudo cloudflared service install
sudo systemctl enable --now cloudflared
```

Visit `https://shamvainnovators.org`. Tailscale can stay installed for private
SSH/admin access — it coexists with the public Cloudflare Tunnel.

> Note: Tailscale Funnel cannot serve a custom domain (only `*.ts.net`), which is
> why a custom domain uses Cloudflare Tunnel instead.

### Updating later

```bash
cd /home/sean/learningPlatform && source venv/bin/activate
git pull
pip install -r requirements.txt
npm run build:css
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart learningplatform
```

## Email (Gmail SMTP)

By default, development prints emails to the **console**. To send real email via Gmail:

1. Copy `.env.example` to `.env` if you have not already.
2. Use a dedicated Gmail or Google Workspace account.
3. Enable **2-Step Verification**, then create an [App Password](https://myaccount.google.com/apppasswords).
4. Set these in `.env`:
   - `EMAIL_HOST_USER` — your Gmail address
   - `EMAIL_HOST_PASSWORD` — the 16-character app password
   - `DEFAULT_FROM_EMAIL` — must use the **same** Gmail address (e.g. `AI Program Zimbabwe <yourprogram@gmail.com>`)
   - `ADMIN_EMAIL` — inbox for contact form submissions (can be the same Gmail)

Verify the setup:

```bash
python manage.py send_test_email your@email.com
```

When `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD` are set, development automatically switches to SMTP. To test verification emails locally, add `REQUIRE_EMAIL_VERIFICATION=True` to `.env`.

### Emails sent by the app

| Trigger | Recipient |
|---------|-----------|
| Registration | Verification link to new user |
| Forgot password / admin reset | Password reset link |
| Account approved / rejected | Applicant |
| Assignment published, grades released, announcements | Students (if notifications enabled) |
| New submission | Teachers |
| Contact form | `ADMIN_EMAIL` |

Verification and reset links use the site URL from the current request. Locally they point to `http://127.0.0.1:8000/...`; in production set `ALLOWED_HOSTS` to your real domain.

Production uses SMTP automatically (`config.settings.production`). Provide the same `.env` email values on the server.
