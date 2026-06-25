document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('form[data-file-upload-form]').forEach(function (form) {
        const input = form.querySelector('input[data-file-upload]');
        const errorEl = form.querySelector('[data-file-upload-error]');
        if (!input) return;

        form.addEventListener('submit', function (e) {
            if (!input.files || !input.files.length) return;
            const file = input.files[0];
            const allowed = (input.dataset.allowedTypes || '').split(',').map(function (s) { return s.trim().toLowerCase(); }).filter(Boolean);
            const maxMb = parseFloat(input.dataset.maxSizeMb || '10');
            const ext = '.' + file.name.split('.').pop().toLowerCase();

            if (allowed.length && allowed.indexOf(ext) === -1) {
                e.preventDefault();
                showError('File type ' + ext + ' is not allowed. Accepted: ' + allowed.join(', '));
                return;
            }
            if (file.size > maxMb * 1024 * 1024) {
                e.preventDefault();
                showError('File must be under ' + maxMb + ' MB.');
                return;
            }
            hideError();
        });

        function showError(msg) {
            if (errorEl) {
                errorEl.textContent = msg;
                errorEl.classList.remove('hidden');
            } else {
                alert(msg);
            }
        }
        function hideError() {
            if (errorEl) errorEl.classList.add('hidden');
        }
    });
});
