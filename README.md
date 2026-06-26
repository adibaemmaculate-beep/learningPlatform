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

PostgreSQL and production deployment config are deferred.

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
