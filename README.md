# Dev Academy — AI & Coding Learning Platform

Django backend with HTML, Tailwind CSS, and JavaScript frontend.

## Quick start

```bash
cd learningPlatform
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_admin
python manage.py runserver
```

Open http://127.0.0.1:8000/

### Default admin credentials

- **Email:** `admin@example.com`
- **Password:** `changeme123`

## Stage 3 — Course Materials, Profiles & Portals

### Student portal (`/student/`)

| URL | Page |
|-----|------|
| `/student/` | Dashboard with greeting, current week, placeholders for assignments |
| `/student/materials/` | Published weekly materials (collapsible weeks) |
| `/student/profile/` | Profile picture + bio (Markdown) |
| `/student/settings/` | Theme, phone, notifications, password |

### Teacher portal (`/teacher/`)

| URL | Page |
|-----|------|
| `/teacher/` | Dashboard with course stats + quick actions |
| `/teacher/materials/` | Manage all weeks (publish/unpublish/delete) |
| `/teacher/materials/create/` | Add new week with PDF uploads |
| `/teacher/materials/<id>/edit/` | Edit week |
| `/teacher/profile/` | Profile picture + bio |
| `/teacher/settings/` | Theme, phone, notifications, password |

### Stage 3 test flow

1. Log in as **teacher** (create teacher invite code from admin if needed)
2. Go to **Course Materials** → **Add Week** → fill in week 1, upload PDFs, check **Publish**
3. Log in as **student** → **Course Materials** → expand week 1, download slides/notes
4. Student **Profile** → upload photo, write bio in Markdown
5. **Settings** → toggle dark mode, update phone number

Assignments, grades, and announcements wire in Stages 4–5.

Emails print to the **console** in development.
