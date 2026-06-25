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

## Stage 1 — Foundation, Auth & Portal Shell

- Invite-code registration with email verification
- Admin approval queue
- Login / logout / forgot password / reset password
- Role-based routing (student, teacher, admin portals)

## Stage 2 — Public Site & Admin Panel

### Public pages

| URL | Page |
|-----|------|
| `/` | Homepage with news section + newsletter signup |
| `/about/` | Program story, team, structure |
| `/students/` | Student showcase (profiles; projects in Stage 5) |
| `/contact/` | Contact form (emails admin via console in dev) |

### Admin panel (`/admin-panel/`)

| URL | Page |
|-----|------|
| `/admin-panel/` | Dashboard + pending approvals |
| `/admin-panel/users/` | User list with filter/search |
| `/admin-panel/users/create-admin/` | Create admin without invite code |
| `/admin-panel/users/<id>/` | User detail + approve/suspend/delete/reset |
| `/admin-panel/invite-codes/` | Generate & deactivate invite codes |
| `/admin-panel/updates/` | News/blog CRUD (shows on homepage) |
| `/admin-panel/settings/` | Theme, notifications, password |

### Stage 2 test flow

1. Visit `/` — public homepage loads
2. Admin → **Updates** → create a published update → refresh `/` to see it in Latest News
3. Footer newsletter signup on homepage
4. `/contact/` — submit form, check terminal for email output
5. `/admin-panel/users/` — filter, view user, suspend/activate, reset password
6. `/admin-panel/invite-codes/` — generate code, deactivate unused codes

Emails print to the **console** in development.
