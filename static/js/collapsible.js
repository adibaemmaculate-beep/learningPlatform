document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-collapsible-toggle]').forEach(function (btn) {
        const targetId = btn.getAttribute('data-collapsible-toggle');
        const panel = document.getElementById(targetId);
        if (!panel) return;
        const chevron = btn.querySelector('.chevron');

        // Once the open transition finishes, drop the fixed height so the panel
        // can grow if its content changes (e.g. images finish loading).
        panel.addEventListener('transitionend', function (e) {
            if (e.propertyName === 'max-height' && panel.classList.contains('open')) {
                panel.style.maxHeight = 'none';
            }
        });

        btn.addEventListener('click', function () {
            const willOpen = !panel.classList.contains('open');
            if (chevron) chevron.classList.toggle('open', willOpen);

            if (willOpen) {
                panel.classList.add('open');
                panel.style.maxHeight = panel.scrollHeight + 'px';
            } else {
                // Pin the current height so the collapse can animate back to 0.
                panel.style.maxHeight = panel.scrollHeight + 'px';
                void panel.offsetHeight; // force reflow
                panel.classList.remove('open');
                panel.style.maxHeight = null;
            }
        });
    });
});
