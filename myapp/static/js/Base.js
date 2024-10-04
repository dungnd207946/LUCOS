document.querySelectorAll('.btnView, .btnTask, .btnSpa, .btnReport').forEach(button => {
    button.addEventListener('click', function () {
        // Tìm phần tử dropdown-content gần nhất
        const dropdown = this.nextElementSibling;

        // Ẩn tất cả các dropdown khác
        document.querySelectorAll('.dropdown-content').forEach(content => {
            if (content !== dropdown) {
                content.parentElement.classList.remove('open');
                content.style.maxHeight = null; // Đặt lại chiều cao
            }
        });

        // Hiển thị hoặc ẩn dropdown hiện tại
        const isOpen = dropdown.parentElement.classList.contains('open');
        if (isOpen) {
            dropdown.parentElement.classList.remove('open');
            dropdown.style.maxHeight = null; // Đặt lại chiều cao về 0
        } else {
            dropdown.parentElement.classList.add('open');
            dropdown.style.maxHeight = dropdown.scrollHeight + 'px'; // Đặt chiều cao bằng với chiều cao thực tế của dropdown
        }
    });
});

document.querySelectorAll('.dropdown').forEach(function(button) {
    button.addEventListener('click', function() {
        const icon = this.querySelector('.icon-collapse');  // Lấy dấu SVG trong button hiện tại


        if (icon.classList.contains('rotate-down')) {
            icon.classList.remove('rotate-down');
        } else {
            icon.classList.add('rotate-down');
        }
    });
});

