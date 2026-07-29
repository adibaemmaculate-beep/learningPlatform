document.addEventListener('DOMContentLoaded', function () {
    const dataEl = document.getElementById('students-data');
    if (!dataEl) return;

    let studentsById = {};
    try {
        const students = JSON.parse(dataEl.textContent);
        studentsById = Object.fromEntries(students.map(function (s) { return [s.id, s]; }));
    } catch (e) {
        return;
    }

    const overlay = document.getElementById('student-overlay');
    const backdrop = document.getElementById('student-overlay-backdrop');
    const closeBtn = document.getElementById('student-overlay-close');
    const avatarEl = document.getElementById('student-overlay-avatar');
    const nameEl = document.getElementById('student-overlay-name');
    const bioEl = document.getElementById('student-overlay-bio');
    const projectEl = document.getElementById('student-overlay-project');

    if (!overlay || !avatarEl || !nameEl || !bioEl || !projectEl) return;

    function renderMarkdown(el, raw) {
        el.dataset.rendered = '';
        el.textContent = raw || '';
        if (typeof marked !== 'undefined' && raw && raw.trim()) {
            el.innerHTML = marked.parse(raw);
            el.dataset.rendered = '1';
        }
    }

    const placeholderUrl = dataEl.dataset.placeholderUrl || '';

    function setAvatar(student) {
        avatarEl.innerHTML = '';
        const img = document.createElement('img');
        img.src = student.profile_pic_url || placeholderUrl;
        img.alt = student.name;
        img.className = 'w-full h-full object-contain';
        avatarEl.appendChild(img);
    }

    function openOverlay(studentId) {
        const student = studentsById[studentId];
        if (!student) return;

        setAvatar(student);
        nameEl.textContent = student.name;
        renderMarkdown(bioEl, student.bio);

        if (student.project_url) {
            projectEl.href = student.project_url;
            projectEl.classList.remove('hidden');
        } else {
            projectEl.href = '#';
            projectEl.classList.add('hidden');
        }

        overlay.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
        closeBtn.focus();
    }

    function closeOverlay() {
        overlay.classList.add('hidden');
        document.body.style.overflow = '';
    }

    document.querySelectorAll('.student-card').forEach(function (card) {
        card.addEventListener('click', function () {
            openOverlay(card.dataset.studentId);
        });
        card.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                openOverlay(card.dataset.studentId);
            }
        });
    });

    closeBtn.addEventListener('click', closeOverlay);
    backdrop.addEventListener('click', closeOverlay);

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && !overlay.classList.contains('hidden')) {
            closeOverlay();
        }
    });
});
