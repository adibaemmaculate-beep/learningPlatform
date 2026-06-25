document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-collapsible-toggle]').forEach(function (btn) {
        btn.addEventListener('click', function () {
            const targetId = btn.getAttribute('data-collapsible-toggle');
            const panel = document.getElementById(targetId);
            const chevron = btn.querySelector('.chevron');
            if (!panel) return;
            panel.classList.toggle('open');
            if (chevron) chevron.classList.toggle('open');
        });
    });
});
