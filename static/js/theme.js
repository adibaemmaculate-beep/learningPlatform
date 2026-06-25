document.addEventListener('DOMContentLoaded', function () {
    const toggle = document.getElementById('theme-toggle');
    const html = document.documentElement;
    if (!toggle) return;

    const profileTheme = html.dataset.userTheme;
    if (profileTheme) {
        html.classList.toggle('dark', profileTheme === 'dark');
        html.classList.toggle('light', profileTheme !== 'dark');
        localStorage.setItem('theme', profileTheme);
    } else {
        const saved = localStorage.getItem('theme');
        if (saved === 'dark') {
            html.classList.remove('light');
            html.classList.add('dark');
        }
    }

    toggle.addEventListener('click', function () {
        const isDark = html.classList.toggle('dark');
        html.classList.toggle('light', !isDark);
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    });
});
