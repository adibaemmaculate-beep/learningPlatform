# Dev Academy — AI & Coding Learning Platform

Django backend with HTML, Tailwind CSS, and JavaScript frontend.

## Stage 1 — Foundation, Auth & Portal Shell

### Quick start

```bash
cd learningPlatform
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_admin
python manage.py runserver
```

Open http://127.0.0.1:8000/auth/login/

### Default admin credentials

- **Email:** `admin@example.com`
- **Password:** `changeme123`

Override via `.env` (copy from `.env.example`).

### Stage 1 features

- Invite-code registration with email verification
- Admin approval queue
- Login / logout / forgot password / reset password
- Role-based routing (student → `/student/`, teacher → `/teacher/`, admin → `/admin-panel/`)
- Minimal invite code generation at `/admin-panel/invite-codes/`
- Portal stub pages for student and teacher

### Test flow

1. Log in as admin → generate a student invite code
2. Register a new student at `/auth/register/` with the invite code
3. Check terminal console for verification email link → open it
4. Admin dashboard → approve the pending user
5. Student logs in → lands on student portal stub

Emails print to the **console** in development (not sent via SMTP).
