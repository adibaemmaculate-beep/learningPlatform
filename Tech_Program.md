This is a really well-scoped program — teaching AI and coding to middle schoolers in Zimbabwe to solve community problems is a meaningful mission, and the platform should reflect that. Here's the full detailed plan:  
---

# Platform Detailed Specification

## AI & Coding Program — Zimbabwe Middle School Cohort

---

## 1\. Platform Overview

A closed, invite-only web platform serving one cohort of middle school students learning AI and coding. Three user types interact with the system: Students, Teachers, and Administrators. The platform handles weekly coursework delivery, assignment submission and grading, student portfolio display, and public-facing program visibility. Everything is scoped to a single course and single cohort for now, with extensibility in mind.  
---

## 2\. User Roles & Permissions

| Action | Student | Teacher | Admin |
| :---- | :---- | :---- | :---- |
| Submit assignments | ✅ | ❌ | ❌ |
| Create/edit assignments | ❌ | ✅ | ❌ |
| Release grades | ❌ | ✅ | ❌ |
| Upload course materials | ❌ | ✅ | ❌ |
| View all student grades | ❌ | ✅ | ✅ |
| Manage users | ❌ | ❌ | ✅ |
| Generate invite codes | ❌ | ❌ | ✅ |
| Approve/delete accounts | ❌ | ❌ | ✅ |
| Post announcements | ❌ | ✅ | ✅ |
| View public site | ✅ | ✅ | ✅ |

---

## 3\. Authentication & Account Creation Flow

### Invite Code System

* Admin generates a unique alphanumeric invite code (e.g., ZW-2025-STU-A3K9) from the admin panel  
* Each code has: a role (student or teacher), an expiry date, a single-use flag, and a status (active / used / expired)  
* Admin can view all generated codes, their status, and who used them

### Registration Flow

1. User visits /register and enters their invite code  
2. Code is validated (correct role, not expired, not already used)  
3. User fills in: first name, last name, email, phone number, password, confirm password  
4. Email verification link is sent — user must verify before proceeding  
5. After email verification, account enters "Pending Approval" state  
6. Admin sees the new user in a pending queue and either approves or deletes them  
7. On approval, user receives an email/SMS confirmation and can log in  
8. On deletion, user receives a polite rejection email

### Login & Session

* Email \+ password login  
* "Forgot password" link on login page → sends reset link via email  
* Sessions expire after a configurable idle period  
* Redirect after login goes to the user's respective portal home

---

## 4\. Database Schema (Full & Revised)

### users

| Field | Type | Notes |
| :---- | :---- | :---- |
| id | UUID | Primary key |
| first\_name | VARCHAR |  |
| last\_name | VARCHAR |  |
| email | VARCHAR | Unique |
| phone\_number | VARCHAR | Optional |
| password\_hash | VARCHAR | Bcrypt |
| type | ENUM | student, teacher, admin |
| status | ENUM | pending, active, suspended |
| email\_verified | BOOLEAN |  |
| email\_verified\_at | TIMESTAMP |  |
| created\_at | TIMESTAMP |  |
| approved\_at | TIMESTAMP | Nullable |
| approved\_by | UUID | FK → users.id |

### invite\_codes

| Field | Type | Notes |
| :---- | :---- | :---- |
| id | UUID |  |
| code | VARCHAR | Unique |
| role | ENUM | student, teacher |
| created\_by | UUID | FK → users.id (admin) |
| used\_by | UUID | FK → users.id, nullable |
| expires\_at | TIMESTAMP |  |
| is\_single\_use | BOOLEAN | Default true |
| status | ENUM | active, used, expired |
| created\_at | TIMESTAMP |  |

### profiles

| Field | Type | Notes |
| :---- | :---- | :---- |
| id | UUID |  |
| user\_id | UUID | FK → users.id |
| bio | TEXT | Student's story |
| profile\_pic\_url | VARCHAR | Stored file path/URL |
| notification\_preferences\_json | JSON | {email: bool, sms: bool} |
| theme | ENUM | light, dark |

### courses

| Field | Type | Notes |
| :---- | :---- | :---- |
| id | UUID |  |
| name | VARCHAR | e.g., "AI & Coding — Cohort 1" |
| description | TEXT |  |
| is\_active | BOOLEAN |  |

### course\_materials

| Field | Type | Notes |
| :---- | :---- | :---- |
| id | UUID |  |
| course\_id | UUID | FK → courses.id |
| week | INTEGER | Week number (1, 2, 3…) |
| title | VARCHAR | e.g., "Week 3: Intro to Machine Learning" |
| description | TEXT | Rich text |
| objectives\_json | JSON | Array of strings |
| slides\_url | VARCHAR | PDF upload |
| notes\_url | VARCHAR | PDF upload |
| other\_resources\_json | JSON | Array of {label, url, type} |
| published | BOOLEAN | Teacher controls visibility |
| created\_at | TIMESTAMP |  |

### assignments

| Field | Type | Notes |
| :---- | :---- | :---- |
| id | UUID |  |
| course\_id | UUID | FK → courses.id |
| title | VARCHAR |  |
| instructions | TEXT | Rich text (supports formatting) |
| week | INTEGER | Which week this belongs to |
| due\_date | TIMESTAMP |  |
| total\_score | INTEGER | Max possible score |
| allowed\_file\_types | JSON | e.g., \[".pdf", ".zip", ".py"\] |
| max\_file\_size\_mb | INTEGER |  |
| grades\_released | BOOLEAN | Default false — teacher controls |
| created\_by | UUID | FK → users.id (teacher) |
| created\_at | TIMESTAMP |  |

### assignment\_submissions

| Field | Type | Notes |
| :---- | :---- | :---- |
| id | UUID |  |
| assignment\_id | UUID | FK → assignments.id |
| student\_id | UUID | FK → users.id |
| file\_url | VARCHAR |  |
| file\_name | VARCHAR | Original filename |
| submitted\_at | TIMESTAMP |  |
| is\_late | BOOLEAN | Auto-computed vs due\_date |
| score\_obtained | INTEGER | Nullable until graded |
| comments | TEXT | Teacher feedback (rich text) |
| graded\_at | TIMESTAMP | Nullable |
| graded\_by | UUID | FK → users.id (teacher) |
| status | ENUM | submitted, graded |

### projects

| Field | Type | Notes |
| :---- | :---- | :---- |
| id | UUID |  |
| student\_id | UUID | FK → users.id |
| title | VARCHAR |  |
| description | TEXT |  |
| write\_up | TEXT | Rich text |
| codebase\_url | VARCHAR | GitHub link or uploaded zip |
| live\_url | VARCHAR | Hosted project link |
| images\_json | JSON | Array of image URLs |
| is\_published | BOOLEAN | Controls public visibility |
| created\_at | TIMESTAMP |  |

### announcements

| Field | Type | Notes |
| :---- | :---- | :---- |
| id | UUID |  |
| title | VARCHAR |  |
| body | TEXT | Rich text |
| created\_by | UUID | FK → users.id |
| visibility | ENUM | everyone, students\_only, teachers\_only, specific\_student |
| target\_student\_id | UUID | FK → users.id, nullable |
| published\_at | TIMESTAMP |  |
| created\_at | TIMESTAMP |  |

### announcement\_reads

| Field | Type | Notes |
| :---- | :---- | :---- |
| id | UUID |  |
| announcement\_id | UUID | FK → announcements.id |
| user\_id | UUID | FK → users.id |
| read\_at | TIMESTAMP |  |

### newsletter

| Field | Type | Notes |
| :---- | :---- | :---- |
| id | UUID |  |
| email | VARCHAR | Unique |
| subscribed\_at | TIMESTAMP |  |

### updates (News/Blog)

| Field | Type | Notes |
| :---- | :---- | :---- |
| id | UUID |  |
| title | VARCHAR |  |
| description | TEXT | Rich text |
| images\_json | JSON | Array of image URLs |
| writer\_id | UUID | FK → users.id |
| published\_at | TIMESTAMP |  |
| created\_at | TIMESTAMP |  |

### audit\_logs

| Field | Type | Notes |
| :---- | :---- | :---- |
| id | UUID |  |
| actor\_id | UUID | FK → users.id |
| action | VARCHAR | e.g., grade\_released, user\_approved |
| target\_type | VARCHAR | e.g., assignment, user |
| target\_id | UUID |  |
| metadata\_json | JSON | Any extra context |
| created\_at | TIMESTAMP |  |

---

## 5\. Student Portal — Page-by-Page

### Home

* Personalized greeting: "Good morning, Tendai 👋"  
* Unread announcements banner — highlights any unseen messages from teachers/admin  
* Work due this week — cards showing assignment title, due date, and a colored status badge: Not Started / Submitted / Graded  
* Recent grade — the most recently returned graded assignment with score  
* Current week indicator — shows which week of the program they're on and links to that week's course materials

### Assignments

* List of all assignments, sorted by due date (upcoming first)  
* Each card shows: title, week number, due date, submission status badge, score (if grades released)  
* Clicking an assignment opens a detail page with:  
  * Title, week, due date  
  * Instructions (rendered rich text)  
  * Allowed file types listed clearly (e.g., "Accepted: .pdf, .py, .zip")  
  * Max file size shown  
  * File upload area — drag and drop or click to browse; validates file type and size before upload  
  * If already submitted: shows submitted file name, submission timestamp, late flag if applicable  
  * If graded and grades released: shows score (e.g., 18 / 20), teacher comments rendered below

### Grades

* Summary bar at top: total score earned vs total possible across all graded assignments, shown as percentage  
* Table listing every assignment with: title, week, due date, submission status, score obtained / total, grade released status  
* If grades are not yet released, score shows as — with a "Grades not yet released" label  
* Visual progress indicator (e.g., a simple bar or ring showing overall standing)

### Course Materials

* Organized by week — each week is a collapsible or card section  
* Each week shows: week title, description, learning objectives as a checklist-style list, download button for slides PDF, download button for notes PDF, and any other resources as labeled links  
* Weeks that haven't been published yet by the teacher are not visible

### Projects

* Student's own final project display  
* Shows: title, description, write-up (rendered rich text), link to codebase, link to live project, images in a small gallery  
* If no project submitted yet, shows a prompt to add one  
* Edit button to update project details

### Profile

* Profile picture (upload/change)  
* Full name (read-only — contact admin to change)  
* Bio / Story (editable text area)  
* Displays their submitted project as a preview card

### Settings

* Theme: light / dark mode toggle  
* Change password: current password, new password, confirm new password  
* Contact details: phone number (editable), email (read-only — shown for reference)  
* Notifications: separate toggles for email notifications and SMS notifications, with a brief description of what each covers (e.g., "New assignment posted," "Grade released," "New announcement")

---

## 6\. Teacher Portal — Page-by-Page

### Home

* Greeting with name  
* Unread / recent announcements they've posted — quick view  
* Assignments needing attention: any assignment past due date where some students haven't been graded yet  
* Pending submissions count: X students have submitted since you last checked  
* Quick actions: "Create Assignment" button, "Post Announcement" button

### Assignments (Teacher View)

* List of all created assignments with: title, week, due date, submission count vs class size (e.g., "12 / 18 submitted"), grades released status  
* Create Assignment button opens a form:  
  * Title  
  * Week (number)  
  * Due date & time picker  
  * Instructions (rich text editor — supports headings, bold, bullet lists, code blocks)  
  * Total score  
  * Allowed file types (multi-select: .pdf, .py, .zip, .ipynb, .docx, .mp4, other)  
  * Max file size  
  * Save as draft or publish  
* Clicking an assignment shows a Submission Tracker:  
  * Table of all students with columns: name, submission status (Submitted / Not Submitted / Late), submission date, file download link, score, graded status  
  * Filter by: all, submitted, not submitted, ungraded  
  * Clicking a student row opens a grading panel: view their submitted file inline (PDF) or download, enter score out of total, write feedback in rich text editor, save grade  
  * Release Grades button — only after clicking this do students see their scores. Can release for all students at once

### Students

* Table of all students ordered by overall grade percentage (descending)  
* Columns: profile picture, name, overall grade %, assignments submitted count, last activity  
* Search bar to find a student by name  
* Clicking a student opens a student detail view:  
  * Profile: picture, name, bio  
  * Grade breakdown: every assignment listed with their score  
  * Submission history: submission dates, late flags  
  * Project preview if submitted

### Progress Dashboard

* Class-wide overview:  
  * Average score per assignment (bar chart)  
  * Grade distribution across the class (histogram)  
  * Submission rate per assignment (how many submitted on time vs late vs not at all)  
  * Top performers and students who may need support (lowest average)  
* Week-by-week completion rates

### Course Materials

* View all uploaded weekly materials in a structured week-by-week list  
* Add Week button — opens a form:  
  * Week number  
  * Title  
  * Description (rich text)  
  * Learning objectives (add multiple as individual lines)  
  * Upload slides PDF  
  * Upload notes PDF  
  * Other resources (add multiple rows with label \+ URL)  
  * Save as draft (not visible to students) or publish  
* Edit and delete options on each week  
* Draft weeks are marked with a "Draft" badge

### Announcements

* Create announcement form: title, body (rich text), visibility (everyone / students only / teachers only / specific student)  
* If "specific student" is selected, a student search dropdown appears  
* List of all posted announcements with: title, date, visibility label, read count (how many students have seen it)

### Profile

* Profile picture (upload/change)  
* Name (read-only)  
* About me / bio (editable)

### Settings

* Same structure as student settings: theme, change password, contact details, notification preferences

---

## 7\. Admin Portal — Page-by-Page

### Home / Dashboard

* Platform stats: total students, total teachers, pending approvals count, assignments created, submissions this week  
* Pending Approvals queue — cards for each user awaiting approval with: name, email, role, registration date, approve / delete buttons  
* Recent audit log entries

### Users

* Full user table: profile pic, name, email, role, status (pending / active / suspended), date joined  
* Filter by: role (student / teacher / admin), status  
* Search by name or email  
* Clicking a user shows full profile detail and actions: approve, suspend, delete, reset password (sends email)  
* Add Admin button — admin can directly create another admin account without an invite code

### Invite Codes

* Table of all generated codes: code string, role, created date, expiry date, status (active / used / expired), used by (name if used)  
* Generate Code button — select role, set expiry date, single-use toggle  
* Deactivate or delete unused codes

### Updates (News Management)

* Create and manage news/blog posts shown on the public homepage  
* Rich text editor for descriptions, image uploads, writer attribution

### Settings

* Theme toggle  
* Change password  
* Platform-level settings (future extensibility placeholder)

---

## 8\. Public Pages — Page-by-Page

### Home (/)

* Hero section: program name, mission statement, strong headline, CTA button ("Learn More" or "Apply")  
* Values section: 3–4 core values with icons and short descriptions  
* Mission & Vision: two-column layout  
* Brief About: 2–3 paragraph overview of the program with a photo  
* News section: latest 3 updates pulled from the updates table, each as a card with title, date, short excerpt, "Read more" link  
* Footer: logo, nav links (Home, About, Meet the Students, Contact), newsletter signup (email input → inserts into newsletter table), social links

### About (/about)

* Full program story: origin, goals, methodology  
* The team: teacher profiles with photo, name, brief bio  
* Program structure overview: how many weeks, what students learn, what the final project is

### Meet the Students (/students)

* Grid of student profile cards showing: profile picture, name, short bio excerpt  
* Clicking a card opens a student page with: full bio, their final project (title, description, write-up, codebase link, live link, images)  
* Only students whose is\_published flag is true on their project appear here  
* This is the public showcase of student work — the most visible output of the program

### Contact (/contact)

* Contact form: name, email, message, send button (emails admin or a configured inbox)  
* Program email and any relevant social handles listed

---

## 9\. Notifications System

Triggered automatically when:

* A new assignment is published → notify all students  
* An assignment due date is 24 hours away → remind students who haven't submitted  
* A submission is received → notify the teacher  
* Grades are released on an assignment → notify the student  
* A new announcement is posted → notify based on visibility setting  
* Account is approved → notify the new user  
* Account is rejected → notify the new user

Each user's notification preferences (set in Settings) determine whether they receive email, SMS, both, or neither for each trigger.  
---

Good choices — Django pairs well with this kind of structured, role-based platform, and keeping file storage local keeps things simple for now. Here's the updated and finalized spec reflecting all your decisions:  
---

## Revised Decisions Log

| Topic | Decision |
| :---- | :---- |
| Rich text | Markdown (stored as plain text, rendered on display) |
| File storage | Local /uploads/ folder within the Django project |
| Backend | Django (Python) |
| Frontend | HTML \+ Tailwind CSS \+ Vanilla JS |
| Notifications | Email only (no SMS) |
| Guest panel | Not on platform |
| SMS | Removed entirely |

---

## Updated Database Schema

Two fields change across the board from the previous spec:  
Removed: notification\_preferences\_json SMS option → replaced with a simpler structure.

### profiles (revised)

| Field | Type | Notes |
| :---- | :---- | :---- |
| id | UUID |  |
| user\_id | UUID | FK → users.id, one-to-one |
| bio | TEXT | Markdown |
| profile\_pic | VARCHAR | Path relative to /uploads/profiles/ |
| theme | ENUM | light, dark — default light |
| email\_notifications | BOOLEAN | Default true |
| updated\_at | TIMESTAMP |  |

### course\_materials (revised)

| Field | Type | Notes |
| :---- | :---- | :---- |
| id | UUID |  |
| course\_id | UUID | FK → courses.id |
| week | INTEGER |  |
| title | VARCHAR |  |
| description | TEXT | Markdown |
| objectives\_json | JSON | Array of strings |
| slides | VARCHAR | Path relative to /uploads/materials/slides/ |
| notes | VARCHAR | Path relative to /uploads/materials/notes/ |
| other\_resources\_json | JSON | Array of {label, url} |
| published | BOOLEAN | Default false |
| created\_at | TIMESTAMP |  |

### assignments (revised)

| Field | Type | Notes |
| :---- | :---- | :---- |
| id | UUID |  |
| course\_id | UUID | FK → courses.id |
| title | VARCHAR |  |
| instructions | TEXT | Markdown |
| week | INTEGER |  |
| due\_date | TIMESTAMP |  |
| total\_score | INTEGER |  |
| allowed\_file\_types | JSON | e.g. \[".pdf", ".py", ".zip"\] |
| max\_file\_size\_mb | INTEGER |  |
| grades\_released | BOOLEAN | Default false |
| is\_draft | BOOLEAN | Default true |
| created\_by | UUID | FK → users.id |
| created\_at | TIMESTAMP |  |

---

## Django Project Structure

project\_root/  
│  
├── manage.py  
├── requirements.txt  
├── .env  
│  
├── config/                        \# Django settings package  
│   ├── settings/  
│   │   ├── base.py  
│   │   ├── development.py  
│   │   └── production.py  
│   ├── urls.py  
│   └── wsgi.py  
│  
├── uploads/                       \# All user-uploaded files live here  
│   ├── profiles/                  \# Profile pictures  
│   ├── materials/  
│   │   ├── slides/                \# Weekly slides PDFs  
│   │   └── notes/                 \# Weekly notes PDFs  
│   ├── submissions/               \# Student assignment file uploads  
│   └── projects/                  \# Project images  
│  
├── apps/  
│   ├── accounts/                  \# User model, auth, invite codes  
│   ├── profiles/                  \# Profile model, settings  
│   ├── courses/                   \# Course and course\_materials models  
│   ├── assignments/               \# Assignment creation, submission, grading  
│   ├── projects/                  \# Student final projects  
│   ├── announcements/             \# Announcements and read receipts  
│   ├── updates/                   \# Public news/blog posts  
│   ├── newsletter/                \# Newsletter subscriptions  
│   ├── notifications/             \# Email notification triggers  
│   ├── audit/                     \# Audit log  
│   └── public/                    \# Public-facing pages (no auth required)  
│  
├── templates/  
│   ├── base.html                  \# Base layout with Tailwind, nav logic  
│   ├── partials/                  \# Reusable components  
│   │   ├── navbar.html  
│   │   ├── sidebar.html  
│   │   ├── announcement\_banner.html  
│   │   └── grade\_badge.html  
│   ├── auth/  
│   │   ├── login.html  
│   │   ├── register.html  
│   │   ├── verify\_email.html  
│   │   ├── forgot\_password.html  
│   │   └── reset\_password.html  
│   ├── student/  
│   │   ├── home.html  
│   │   ├── assignments.html  
│   │   ├── assignment\_detail.html  
│   │   ├── grades.html  
│   │   ├── course\_materials.html  
│   │   ├── projects.html  
│   │   └── profile.html  
│   ├── teacher/  
│   │   ├── home.html  
│   │   ├── assignments.html  
│   │   ├── assignment\_detail.html  
│   │   ├── submission\_tracker.html  
│   │   ├── grade\_submission.html  
│   │   ├── students.html  
│   │   ├── student\_detail.html  
│   │   ├── progress.html  
│   │   ├── course\_materials.html  
│   │   └── announcements.html  
│   ├── admin/  
│   │   ├── home.html  
│   │   ├── users.html  
│   │   ├── user\_detail.html  
│   │   ├── invite\_codes.html  
│   │   └── updates.html  
│   └── public/  
│       ├── home.html  
│       ├── about.html  
│       ├── students.html  
│       ├── student\_public.html  
│       └── contact.html  
│  
└── static/  
    ├── css/  
    │   └── main.css               \# Compiled Tailwind output  
    ├── js/  
    │   ├── theme.js               \# Dark/light mode toggle  
    │   ├── markdown.js            \# Markdown renderer (e.g. marked.js via CDN)  
    │   ├── file\_upload.js         \# File type \+ size validation before submit  
    │   └── notifications.js       \# Dismiss/read announcement logic  
    └── images/  
        └── logo.svg

---

## Django Apps — What Each Owns

### accounts

* Custom User model (extends AbstractBaseUser)  
* InviteCode model  
* Views: register, login, logout, verify email, forgot password, reset password  
* Logic: invite code validation, email verification token generation, password reset token  
* Middleware: role-based redirect after login (student → /student/, teacher → /teacher/, admin → /admin/)

### profiles

* Profile model (one-to-one with User)  
* Auto-created via Django signal when a user is approved  
* Views: view profile, edit profile, update settings, change password  
* File handling: profile picture upload → saved to /uploads/profiles/{user\_id}/

### courses

* Course model  
* CourseMaterial model  
* Teacher views: list materials, create week, edit week, delete week, toggle published  
* Student views: list published materials by week  
* File handling: slides/notes PDFs → /uploads/materials/slides/ and /uploads/materials/notes/

### assignments

* Assignment model  
* AssignmentSubmission model  
* Teacher views: create, edit, delete assignment; view submission tracker; grade a submission; release grades  
* Student views: view assignment list; view assignment detail; submit file; view grade if released  
* File handling: student submissions → /uploads/submissions/{assignment\_id}/{student\_id}/  
* Auto-flag: is\_late computed at submission time by comparing submitted\_at to due\_date

### projects

* Project model  
* Student views: create/edit their own project  
* Teacher views: view all projects  
* Public views: published projects on /students/  
* File handling: project images → /uploads/projects/{student\_id}/

### announcements

* Announcement model  
* AnnouncementRead model  
* Teacher/Admin views: create announcement, view read receipts  
* Student views: view announcements targeted to them; mark as read (auto on open)

### updates

* Update model (news/blog posts for public homepage)  
* Admin views: create, edit, delete updates  
* Public views: latest 3 shown on homepage, full list optionally on about page

### newsletter

* Newsletter model (just email)  
* Public view: form submission on homepage footer  
* Validates email, prevents duplicates, no confirmation email required (keep it simple)

### notifications

* No model — this is a service layer  
* EmailNotificationService class with methods like:  
  * notify\_assignment\_published(assignment)  
  * notify\_grade\_released(submission)  
  * notify\_account\_approved(user)  
  * notify\_account\_rejected(user)  
  * notify\_announcement(announcement)  
  * notify\_submission\_received(submission) → to teacher  
  * notify\_due\_date\_reminder() → runs via Django management command or cron  
* Uses Django's built-in send\_mail backed by an SMTP config in settings  
* Each method checks the recipient's email\_notifications preference before sending

### audit

* AuditLog model  
* Simple log\_action(actor, action, target\_type, target\_id, metadata) utility function  
* Called from views at key moments: grade released, user approved, user deleted, invite code generated, material published

### public

* No models — view-only app  
* Views for: home, about, meet the students, contact  
* Contact form sends email to admin inbox via send\_mail

---

## URL Structure

/                          → public home  
/about/                    → public about  
/students/                 → public meet the students  
/students/\<student\_id\>/    → public student profile \+ project  
/contact/                  → public contact form

/auth/login/               → login  
/auth/register/            → register with invite code  
/auth/verify/\<token\>/      → email verification  
/auth/forgot-password/     → forgot password  
/auth/reset/\<token\>/       → reset password

/student/                  → student home  
/student/assignments/      → assignment list  
/student/assignments/\<id\>/ → assignment detail \+ submission  
/student/grades/           → grades overview  
/student/materials/        → course materials by week  
/student/project/          → student's own project  
/student/profile/          → profile view/edit  
/student/settings/         → settings

/teacher/                  → teacher home  
/teacher/assignments/      → assignment list \+ create  
/teacher/assignments/\<id\>/ → assignment detail \+ submission tracker  
/teacher/assignments/\<id\>/grade/\<submission\_id\>/ → grade a submission  
/teacher/students/         → all students table  
/teacher/students/\<id\>/    → student detail  
/teacher/progress/         → class progress dashboard  
/teacher/materials/        → course materials management  
/teacher/announcements/    → create \+ view announcements  
/teacher/profile/          → teacher profile  
/teacher/settings/         → settings

/admin-panel/              → admin home (use /admin-panel/ not /admin/ to avoid clash with Django admin)  
/admin-panel/users/        → user management  
/admin-panel/users/\<id\>/   → user detail \+ actions  
/admin-panel/invite-codes/ → manage invite codes  
/admin-panel/updates/      → manage news posts  
/admin-panel/settings/     → settings

---

## File Upload Rules

| Upload type | Folder | Allowed types | Max size |
| :---- | :---- | :---- | :---- |
| Profile picture | /uploads/profiles/ | .jpg, .jpeg, .png, .webp | 2 MB |
| Slides (PDF) | /uploads/materials/slides/ | .pdf | 20 MB |
| Notes (PDF) | /uploads/materials/notes/ | .pdf | 20 MB |
| Assignment submission | /uploads/submissions/ | Configured per assignment | Configured per assignment |
| Project images | /uploads/projects/ | .jpg, .jpeg, .png, .webp | 5 MB each |

Validation happens at two levels: client-side (JS checks file type and size before the form submits, gives instant feedback) and server-side (Django form/view re-validates — client checks are convenience only, never trusted).  
---

## Email Notification Templates

Each email is plain but clearly structured. All use a consistent layout: program logo text header, greeting, body, CTA button or link, footer with program name.

| Trigger | Subject | Recipient |
| :---- | :---- | :---- |
| Account approved | "Your account has been approved" | New user |
| Account rejected | "Update on your application" | Rejected user |
| Email verification | "Verify your email address" | Registering user |
| Password reset | "Reset your password" | Requesting user |
| New assignment published | "New assignment: \[title\]" | All students |
| Assignment due in 24hrs | "Reminder: \[title\] is due tomorrow" | Students who haven't submitted |
| Submission received | "\[Student name\] submitted \[assignment title\]" | Teacher |
| Grade released | "Your grade for \[title\] is available" | Student |
| New announcement | "New announcement: \[title\]" | Based on visibility |

---

Perfect. Hosting on your own server with Django \+ SMTP keeps everything self-contained. Here's the final piece of the spec covering deployment and environment configuration:  
---

## Deployment & Server Specification

### Server Setup

* OS: Ubuntu 24.04 LTS (recommended)  
* Web server: Nginx — handles static files, media/uploads, and proxies requests to Gunicorn  
* Application server: Gunicorn — runs the Django app as a WSGI process  
* Process manager: Systemd — keeps Gunicorn running, restarts on crash  
* Database: PostgreSQL (strongly recommended over SQLite for a live multi-user platform)  
* SSL: Let's Encrypt via Certbot — free HTTPS for your domain

### How Requests Flow

Browser  
  ↓  
Nginx (port 443, SSL)  
  ├── /static/  → served directly from disk by Nginx (fast, no Django involved)  
  ├── /uploads/ → served directly from disk by Nginx (your uploaded files)  
  └── everything else → proxied to Gunicorn → Django

### /uploads/ on Your Own Server

Since you're self-hosting, the uploads folder lives directly on your server's disk. Nginx serves those files statically just like it serves your CSS and JS — Django doesn't touch them on read, only on write (when a file is first uploaded). In your Django settings this maps to MEDIA\_ROOT and MEDIA\_URL:  
\# settings/base.py  
MEDIA\_ROOT \= BASE\_DIR / 'uploads'  
MEDIA\_URL \= '/uploads/'

Nginx config will have a block like:  
location /uploads/ {  
    alias /path/to/your/project/uploads/;  
}

### Environment Variables (.env)

Everything sensitive lives here, never in code:  
SECRET\_KEY=your-django-secret-key  
DEBUG=False  
ALLOWED\_HOSTS=yourdomain.com,www.yourdomain.com

\# Database  
DB\_NAME=yourdbname  
DB\_USER=yourdbuser  
DB\_PASSWORD=yourdbpassword  
DB\_HOST=localhost  
DB\_PORT=5432

\# Email (SMTP)  
EMAIL\_HOST=smtp.gmail.com  
EMAIL\_PORT=587  
EMAIL\_USE\_TLS=True  
EMAIL\_HOST\_USER=yourprogramemail@gmail.com  
EMAIL\_HOST\_PASSWORD=your-app-password  
DEFAULT\_FROM\_EMAIL=AI Program Zimbabwe \<yourprogramemail@gmail.com\>  
ADMIN\_EMAIL=admin@yourdomain.com

\# File uploads  
MEDIA\_ROOT=/path/to/your/project/uploads  
MAX\_UPLOAD\_SIZE\_MB=20

### requirements.txt

django\>=4.2  
psycopg2-binary          \# PostgreSQL adapter  
python-dotenv            \# Load .env file  
Pillow                   \# Image handling for profile pictures  
python-markdown          \# Server-side markdown (for emails, since marked.js handles browser rendering)  
django-widget-tweaks     \# Cleaner form rendering in templates  
whitenoise               \# Serves static files efficiently (optional but useful)  
gunicorn                 \# Production WSGI server

---

## Final Complete Spec Summary

Here is everything locked in, in one place:

### Technology

| Layer | Choice |
| :---- | :---- |
| Backend | Django 4.2+ |
| Frontend | HTML \+ Tailwind CSS \+ Vanilla JS |
| Database | PostgreSQL |
| File storage | Local /uploads/ folder |
| Markdown (browser) | marked.js via CDN |
| Markdown (server) | python-markdown (for emails only) |
| Email | SMTP (Gmail or equivalent) |
| Web server | Nginx \+ Gunicorn |
| SSL | Let's Encrypt |
| Server OS | Ubuntu 24.04 |

### What the Platform Does

| Feature | Included |
| :---- | :---- |
| Invite code registration | ✅ |
| Email verification | ✅ |
| Admin approval queue | ✅ |
| Role-based portals (student/teacher/admin) | ✅ |
| Weekly course materials (slides \+ notes PDFs) | ✅ |
| Assignment creation with rich instructions | ✅ |
| File type \+ size restrictions per assignment | ✅ |
| Student file submission | ✅ |
| Late submission detection | ✅ |
| Submission status tracking | ✅ |
| Score-based grading with comments | ✅ |
| Grade release control (teacher decides when) | ✅ |
| Student progress dashboard for teachers | ✅ |
| One-way announcements (teacher/admin → students) | ✅ |
| Announcement read receipts | ✅ |
| Student final projects | ✅ |
| Public site (home, about, meet students, contact) | ✅ |
| Student projects publicly displayed | ✅ |
| Newsletter signup | ✅ |
| News/updates section | ✅ |
| Dark/light mode | ✅ |
| Email notifications (opt-in per user) | ✅ |
| Audit log | ✅ |
| Django admin panel (dev/superuser) | ✅ |
| SMS | ❌ |
| Guest speaker section | ❌ |
| Multiple cohorts/courses | ❌ (future) |

---

This spec is now complete and ready to hand to a developer or start building from yourself. The logical build order I'd suggest is:

1. Django project scaffolding \+ settings \+ .env  
2. accounts app — User model, invite codes, registration, email verification, approval  
3. Role-based routing and base templates  
4. profiles app  
5. courses app — course materials by week  
6. assignments app — creation, submission, grading, grade release  
7. projects app  
8. announcements app  
9. notifications service layer  
10. public app — all public pages  
11. updates \+ newsletter  
12. audit app  
13. Frontend polish — Tailwind styling, dark mode, marked.js integration, JS file validation  
14. Nginx \+ Gunicorn deployment configuration

