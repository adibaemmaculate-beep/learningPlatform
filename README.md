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

## Stage 4 — Assignments, Grades & Progress

### Student portal (`/student/`)

| URL | Page |
|-----|------|
| `/student/` | Dashboard with due-this-week assignments and overall grade |
| `/student/assignments/` | List of published assignments + submission status |
| `/student/assignments/<id>/` | View instructions, submit file (validated client + server) |
| `/student/grades/` | Grade breakdown (visible after teacher releases grades) |
| `/student/materials/` | Published weekly materials |
| `/student/profile/` | Profile picture + bio (Markdown) |
| `/student/settings/` | Theme, phone, notifications, password |

### Teacher portal (`/teacher/`)

| URL | Page |
|-----|------|
| `/teacher/` | Dashboard with assignment stats + needs-attention list |
| `/teacher/assignments/` | Manage all assignments |
| `/teacher/assignments/create/` | Create assignment (file rules, due date, publish) |
| `/teacher/assignments/<id>/` | Submission tracker with filters |
| `/teacher/assignments/<id>/grade/<submission_id>/` | Grade submission + feedback |
| `/teacher/students/` | Class roster with search |
| `/teacher/students/<id>/` | Student profile + grade breakdown |
| `/teacher/progress/` | Class progress dashboard |
| `/teacher/materials/` | Manage weekly course materials |

### Stage 4 test flow

1. Log in as **teacher** → **Assignments** → **Create Assignment**
2. Set title, week, due date, instructions, allowed file types (e.g. `.pdf`), check **Publish**
3. Log in as **student** → **Assignments** → open assignment → upload a valid file
4. Teacher → assignment detail → **Grade** submission → enter score + feedback
5. Teacher → **Release Grades** on the assignment
6. Student → **Grades** → verify score appears
7. Teacher → **Students** / **Progress** → verify roster and stats

Announcements and notifications wire in Stage 5.

Emails print to the **console** in development.
