import BaseCustomerInfor from "./infor-customer.js";
class SpaCustomer extends BaseCustomerInfor{
    constructor() {
        super();
    }
    abstractShowDetail(id) {
        window.location.href = "/spa/detail/" + id;
    }
}
const ctm = new SpaCustomer();
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
                    const cardId = row.getAttribute('data-card-id');
                    ctm.abstractShowDetail(cardId); // Gọi hàm hiển thị chi tiết với userId tương ứng
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

// Lấy modal
var modal = document.getElementById("myModal");

// Lấy nút để mở modal
var btn = document.getElementById("openModalBtn");

// Lấy phần tử <span> để đóng modal
var span = document.getElementsByClassName("close")[0];

// Khi người dùng bấm vào nút, mở modal
btn.onclick = function() {
    modal.style.display = "block";
}

// Khi người dùng bấm vào <span> (x), đóng modal
span.onclick = function() {
    modal.style.display = "none";
}

// Khi người dùng bấm ra ngoài modal, đóng modal
// window.onclick = function(event) {
//     if (event.target == modal) {
//         modal.style.display = "none";
//     }
// }
