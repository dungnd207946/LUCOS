import BaseCustomerInfor from "./infor-customer.js";
class Customer extends BaseCustomerInfor{
        constructor() {
            super();
        }
        abstractShowDetail(id) {
            window.location.href = "/khach-hang/infor-khach-hang/" + id;
        }
}

const ctm = new Customer();
// Hàm để gọi showDetail nếu không phải click chuột vaào checkbox
document.addEventListener("DOMContentLoaded", function() {
        // Lấy tất cả các hàng trong bảng
    const rows = document.querySelectorAll('.value');

    // Duyệt qua từng hàng và gán sự kiện onclick
    rows.forEach(row => {
        row.addEventListener('click', function(event) {
            const targetCell = event.target.closest('td')
            if (targetCell) {
                // Kiểm tra xem ô này có chứa checkbox không
                const checkbox = targetCell.querySelector('input[type="checkbox"]');

                if (checkbox) {
                    // Nếu ô này chứa checkbox, kiểm tra trạng thái của checkbox
                    if (checkbox.checked) {
                        row.classList.add('row-selected'); // Thêm lớp nếu checkbox được chọn
                    } else {
                        row.classList.remove('row-selected'); // Xóa lớp nếu checkbox bị bỏ chọn
                    }
                } else {
                    // Nếu ô này không chứa checkbox, thực hiện hành động hiển thị chi tiết
                    const userId = row.getAttribute('data-user-id');
                    ctm.abstractShowDetail(userId); // Gọi hàm hiển thị chi tiết với userId tương ứng
                }
            }
        });
    });
});

document.getElementById('allCheckBox').addEventListener('click', function(event){
    ctm.toggleSelectAll(event.target)
})

document.querySelectorAll('.eachCheckBox').forEach(element => {
    element.addEventListener('click', () => {
        ctm.toggleDeleteButton();
    });
});

function confirmDelete() {
    return confirm('Xác nhận xóa khách hàng này?');
}
