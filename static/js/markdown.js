(function () {
    if (typeof marked === 'undefined') {
        return;
    }

    const renderer = new marked.Renderer();

    renderer.image = function (token) {
        const href = token.href || '';
        const title = token.title || '';
        const text = token.text || '';
        const caption = text || title;
        const escapedCaption = caption
            .replace(/&/g, '&amp;')
            .replace(/"/g, '&quot;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');

        if (caption) {
            return (
                '<figure class="update-figure">' +
                '<img src="' + href + '" alt="' + escapedCaption + '">' +
                '<figcaption>' + escapedCaption + '</figcaption>' +
                '</figure>'
            );
        }
        return (
            '<figure class="update-figure">' +
            '<img src="' + href + '" alt="">' +
            '</figure>'
        );
    };

    marked.use({
        gfm: true,
        breaks: true,
        renderer: renderer,
    });

    document.addEventListener('DOMContentLoaded', function () {
        document.querySelectorAll('.markdown-content').forEach(function (el) {
            if (el.dataset.rendered) {
                return;
            }
            const raw = el.textContent || el.innerText;
            if (raw.trim()) {
                el.innerHTML = marked.parse(raw);
                el.dataset.rendered = '1';
            }
        });
    });
})();
