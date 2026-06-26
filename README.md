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
| **Email notifications** | Assignment published, submission received, grades released, announcements, account approved/rejected (console in dev) |

### Stage 5 test flow

1. **Teacher** → Announcements → Post (try "Students only" visibility)
2. **Student** → see banner on dashboard → open announcement (marks as read)
3. **Student** → My Project → fill details, upload images, check **Publish**
4. Visit **/students/** → click student card → verify public project page
5. **Teacher** → Projects → view student project
6. Toggle **email notifications** off in Settings → trigger an announcement → confirm no console email for that user

PostgreSQL and production deployment config are deferred.

Emails print to the **console** in development.
