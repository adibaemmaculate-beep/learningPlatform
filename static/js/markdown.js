document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.markdown-content').forEach(function (el) {
        if (el.dataset.rendered) return;
        const raw = el.textContent || el.innerText;
        if (typeof marked !== 'undefined' && raw.trim()) {
            el.innerHTML = marked.parse(raw);
            el.dataset.rendered = '1';
        }
    });
});
