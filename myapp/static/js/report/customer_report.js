import BaseCustomerInfor from "../infor-customer.js";
class CustomerReport extends BaseCustomerInfor{
    constructor() {
        super();
    }
    abstractShowDetail(id) {
        window.location.href = "";
    }
    toggleCheckbox(td) {
        var checkbox = td.querySelector('input[type="checkbox"]');
        if (checkbox) {
            checkbox.checked = !checkbox.checked;  // Đảo trạng thái checkbox
        }
    }
}
const ctm = new CustomerReport();
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
                }
            }
        });
    });
});

document.getElementById('allCheckBox').addEventListener('click', function(event){
    ctm.toggleSelectAll(event.target)
    console.log("Check all")
})

document.querySelectorAll('.eachCheckBox').forEach(element => {
    element.addEventListener('click', () => {
        ctm.toggleDeleteButton();
    });
});

