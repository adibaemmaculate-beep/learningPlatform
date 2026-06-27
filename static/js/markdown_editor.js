(function () {
    function getCsrfToken() {
        const input = document.querySelector('[name=csrfmiddlewaretoken]');
        return input ? input.value : '';
    }

    function getCodeMirror(editor) {
        return editor.codemirror || editor;
    }

    function syncEditorToTextarea(editor, textarea) {
        textarea.value = editor.value();
    }

    function insertColor(editor) {
        const cm = getCodeMirror(editor);
        const selected = cm.getSelection();
        const color = window.prompt('Enter a color (hex, e.g. #2563eb):', '#2563eb');
        if (!color) {
            return;
        }
        const text = selected || 'colored text';
        cm.replaceSelection('<span style="color: ' + color + '">' + text + '</span>');
        cm.focus();
    }

    function insertLineBreak(editor) {
        const cm = getCodeMirror(editor);
        const cursor = cm.getCursor();
        cm.replaceRange('\n\n', cursor);
        cm.setCursor({ line: cursor.line + 2, ch: 0 });
        cm.focus();
    }

    function createUploadImageAction(uploadUrl) {
        return function uploadImage(editor) {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = '.jpg,.jpeg,.png,.webp';
            input.onchange = function () {
                const file = input.files[0];
                if (!file) {
                    return;
                }
                const formData = new FormData();
                formData.append('image', file);
                fetch(uploadUrl, {
                    method: 'POST',
                    headers: { 'X-CSRFToken': getCsrfToken() },
                    body: formData,
                })
                    .then(function (response) {
                        return response.json().then(function (data) {
                            if (!response.ok) {
                                throw new Error(data.error || 'Upload failed.');
                            }
                            return data;
                        });
                    })
                    .then(function (data) {
                        const cm = getCodeMirror(editor);
                        const caption = window.prompt('Image caption (optional):', '') || '';
                        const escaped = caption
                            .replace(/&/g, '&amp;')
                            .replace(/"/g, '&quot;')
                            .replace(/</g, '&lt;')
                            .replace(/>/g, '&gt;');
                        let html = '<figure class="update-figure">\n  <img src="' + data.url + '"';
                        if (caption) {
                            html += ' alt="' + escaped + '">\n  <figcaption>' + escaped + '</figcaption>';
                        } else {
                            html += ' alt="">';
                        }
                        html += '\n</figure>\n\n';
                        cm.replaceSelection(html);
                        cm.focus();
                    })
                    .catch(function (error) {
                        window.alert(error.message || 'Image upload failed.');
                    });
            };
            input.click();
        };
    }

    function buildToolbar(uploadUrl) {
        const toolbar = [
            'bold',
            'italic',
            'strikethrough',
            '|',
            {
                name: 'line-break',
                action: insertLineBreak,
                className: 'easymde-line-break',
                title: 'Line break (new paragraph)',
            },
            '|',
            'heading',
            'quote',
            'unordered-list',
            'ordered-list',
            '|',
            'link',
        ];

        if (uploadUrl) {
            toolbar.push({
                name: 'upload-image',
                action: createUploadImageAction(uploadUrl),
                className: 'easymde-upload-image',
                title: 'Upload image',
            });
        } else {
            toolbar.push('image');
        }

        toolbar.push(
            '|',
            'horizontal-rule',
            'code',
            '|',
            {
                name: 'color',
                action: insertColor,
                className: 'easymde-color',
                title: 'Text color',
            },
            '|',
            'preview',
            'side-by-side',
            'fullscreen'
        );

        return toolbar;
    }

    function initEditors() {
        if (typeof EasyMDE === 'undefined') {
            return;
        }

        document.querySelectorAll('textarea[data-markdown-editor]').forEach(function (textarea) {
            if (textarea.dataset.editorInitialized) {
                return;
            }

            const uploadUrl = textarea.dataset.markdownEditorUploadUrl || '';
            const editor = new EasyMDE({
                element: textarea,
                spellChecker: false,
                status: false,
                autofocus: false,
                minHeight: '200px',
                toolbar: buildToolbar(uploadUrl),
                previewClass: ['markdown-content', 'font-body-md'],
                renderingConfig: {
                    singleLineBreaks: true,
                },
            });

            const form = textarea.closest('form');
            if (form) {
                form.addEventListener('submit', function () {
                    syncEditorToTextarea(editor, textarea);
                });
            }

            textarea.dataset.editorInitialized = '1';
            textarea.easyMDEInstance = editor;
        });
    }

    document.addEventListener('DOMContentLoaded', initEditors);
})();
