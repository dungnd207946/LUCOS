export default class BaseCustomerInfor {
    constructor() {
        if (new.target === BaseCustomerInfor) {
            throw new Error("Cannot instantiate an abstract class.");
        }
    }
    toggleDeleteButton() {
        var deleteButton = document.getElementById("button-box");
        var anyChecked = false;
        var checkboxes = document.getElementsByName("selected_customers");
        for (var i = 0; i < checkboxes.length; i++) {
            if (checkboxes[i].checked) {
                anyChecked = true;
                break;
            }
        }
        if (anyChecked) {
            deleteButton.style.display = "inline-block";
            deleteButton.classList.add("fade-in");
        } else {
            deleteButton.classList.remove("fade-in");
            setTimeout(function() {
                deleteButton.style.display = "none";
            }, 300); // Thời gian delay để hoàn thành animation
        }
    }
    confirmDelete() {
        return confirm("Bạn có chắc chắn muốn xóa khách hàng này?");
    }

    toggleSelectAll(source) {
        console.log("Checkbox all")
        const checkboxes = document.querySelectorAll('tbody .checkbox-custom');
        checkboxes.forEach(checkbox => {
            checkbox.checked = source.checked;
        });
        this.toggleDeleteButton();
    }

    abstractShowDetail(id){
         throw new Error("Abstract method must be implemented in derived class");
    }
}
