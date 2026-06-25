document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.announcement-dismiss').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var item = btn.closest('.announcement-item');
            if (item) {
                item.remove();
            }
            var banner = document.getElementById('announcement-banner');
            if (banner && banner.children.length === 0) {
                banner.remove();
            }
        });
    });
});
