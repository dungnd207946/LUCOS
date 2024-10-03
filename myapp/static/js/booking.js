
// Tạo các mốc thời gian

function generateTimeSlots(staffs) {
    return new Promise((resolve, reject) => {
        // Tạo bảng và các phần của bảng
        const table = document.createElement('table');
        table.innerHTML = ''
        table.classList.add('schedule-table');

        const thead = document.createElement('thead');
        const headRow = document.createElement('tr');

        // Tạo các ô tiêu đề
        const timeHeader = document.createElement('th');
        timeHeader.textContent = 'Time';
        timeHeader.classList.add('time-header');
        headRow.appendChild(timeHeader);

        staffs.forEach(function (s) {
            const staffHeader = document.createElement('th');
            staffHeader.textContent = s.name;
            staffHeader.id = s.id;
            staffHeader.classList.add('staff-header');
            headRow.appendChild(staffHeader);
        })
        thead.id = 'schedule-head'
        thead.appendChild(headRow);
        table.appendChild(thead);

        const tbody = document.createElement('tbody');
        tbody.id = 'schedule-body';

        let startTime = new Date();
        startTime.setHours(9, 0, 0); // Set start time to 9:00 AM

        for (let i = 0; i < 50; i++) { // 40 slots for 15 minutes each
            const timeString = startTime.toTimeString().substring(0, 5);
            const row = document.createElement('tr');
            const timeCell = document.createElement('td');
            timeCell.textContent = timeString;
            timeCell.classList.add('time-cell');
            row.appendChild(timeCell);

            //Tạo bảng trắng
            staffs.forEach(function (s) {
                const emptyCell = document.createElement('td');
                emptyCell.classList.add('staff-cell');
                row.appendChild(emptyCell);
            })

            tbody.appendChild(row);

            startTime.setMinutes(startTime.getMinutes() + 15); // Increment by 15 minutes
        }

        table.appendChild(tbody);

        // Thêm bảng vào container
        const tableContainer = document.getElementById('table-container');
        tableContainer.innerHTML = '';
        tableContainer.appendChild(table);

        resolve(); // Báo hiệu là generateTimeSlots đã hoàn thành
    });
}

//Hàm đặt mặc định nếu chưa chọn ngày thì sẽ là ngày hôm nay
document.addEventListener('DOMContentLoaded', (event) => {
    const dateInput = document.getElementById('schedule-date');
    if (!dateInput.value) {
        const today = new Date();
        const day = String(today.getDate()).padStart(2, '0');
        const month = String(today.getMonth() + 1).padStart(2, '0'); // January is 0
        const year = today.getFullYear();
        const todayStr = `${year}-${month}-${day}`;
        dateInput.value = todayStr;
    }
    filterScheduleByDate();
});
// Hàm để chuyển đổi định dạng ngày
function formatDate(dateString) {
    const date = new Date(dateString);
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${day}/${month}/${year}`;
}

// Hàm showCard được thêm vào 2 hàm get suggestion, khi chọn suggestion sẽ auto gọi showCard
async function showCard(customer_id) {
    const cardContainer = document.getElementById('customer-card-container');
    cardContainer.innerHTML = '<p style="font-weight: bold">Các thẻ đang sử dụng</p>';
    let hasMatchingCard = false;

    try {
        // Fetch tất cả các card
        const response = await fetch('/get-all-card');
        const data = await response.json();

        for (const c of data.card) {
            if (c.customer_id === customer_id) {
                console.log(c.id);
                hasMatchingCard = true;
                cardContainer.innerHTML += `<div class="card" id="card-${c.id}">
                    <div style="font-weight: bold;">Số thẻ ${c.id}</div>
                    <input type="hidden" id="card-id" name="card_id" value="">
                </div>`;

                const treatmentContainer = document.getElementById(`card-${c.id}`);

                // Fetch treatment cho từng card và chờ kết quả
                const treatmentResponse = await fetch('/get-treatment-by-card?card_id=' + c.id);
                const treatmentData = await treatmentResponse.json();

                treatmentData.treatment.forEach(t => {
                    treatmentContainer.innerHTML += `<div class="treatment-line">
                        <label style="display: flex; width: 100%">
                        <div class="treatment-name">${t.name}:</div>
                        <div class="treatment-detail">Đã dùng: ${t.time_used} / ${t.total_time} buổi</div>
                        <div class="treatment-radio">
                            <input class="select-treatment" type="radio" id="radio-box-${t.treatment_id}" name="treatment_id" value="${t.treatment_id}" data-card-id="${c.id}" required>
                        </div>
                        </label>
                    </div>`;
                    if (parseInt(t.time_used) >= parseInt(t.total_time)) {
                        const tick_box = document.getElementById("radio-box-" + t.treatment_id);
                        tick_box.style.display = 'none';
                        console.log("Thẻ " + t.name + " hết lượt");
                    }
                });
            }
        }

        // Cập nhật hiển thị cardContainer
        if (hasMatchingCard) {
            cardContainer.style.display = 'block';
        } else {
            cardContainer.innerHTML = '<p style="font-weight: bold; color: #dc3545">Khách hàng này chưa có thẻ !</p>';
            cardContainer.style.display = 'block';
        }

        // Gán sự kiện cho các radio
        document.querySelectorAll('.select-treatment').forEach(radio => {
            radio.addEventListener('change', function() {
                const cardId = this.getAttribute('data-card-id');
                console.log('Selected card_id:', cardId);
                document.getElementById('card-id').value = cardId;
                console.log('Selected card_id again:', cardId);
            });
        });

    } catch (error) {
        console.error('Error:', error);
    }
}


var ID = ''

// Hàm xử lí data được truyền vào để đưa ra suggestion phù hợp
function showSuggestion(data){
    const suggestionsDiv = document.getElementById('suggestions');
    suggestionsDiv.innerHTML = '';
        if (data.suggestions.length > 0) {
            data.suggestions.forEach(suggestion => {
                const suggestionElement = document.createElement('a');
                suggestionElement.setAttribute('href', '#');
                suggestionElement.classList.add('list-group-item', 'list-group-item-action');
                suggestionElement.innerHTML = '<strong>' + suggestion.customer_id + '</strong><br>' + suggestion.name;
                suggestionElement.addEventListener('click', () => {
                    document.getElementById('customer_id').value = suggestion.name;
                    // Tùy thuộc vào cách bạn xây dựng API, bạn có thể lấy được customer_id từ đối tượng suggestion
                    const customerId = suggestion.customer_id;
                    ID = customerId
                    console.log('Customer ID:', customerId);
                    suggestionsDiv.style.display = 'none';
                    console.log(customerId)
                    showCard(customerId);
                });
                suggestionsDiv.appendChild(suggestionElement);
            });
            suggestionsDiv.style.display = 'block';
        } else {
            suggestionsDiv.style.display = 'none';
        }
}

// Hàm Lấy suggestion thông qua việc nhập input
function getSpaSuggestions(input) {
    if (input.toString() === ''){
        const cardContainer = document.getElementById('customer-card-container');
        cardContainer.style.display = 'none'
    }
    fetch('/get-spa-customer-suggestions?input=' + input)
        .then(response => response.json())
        .then(data => {
            showSuggestion(data)
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

// Hàm dùng khi chọn ô input sẽ tự động xuất hiện suggestion
function showAllSpaSuggestions(input) {
    if (input.toString() === ''){
        fetch('/get-all-spa-customer-suggestions')
        .then(response => response.json())
        .then(data => {
            showSuggestion(data);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    } // Không có ký tự nào
    else {
        getSpaSuggestions(input);
    }
}

function getSuggestions(input) {
    fetch('/get-customer-suggestions?input=' + input)
        .then(response => response.json())
        .then(data => {
            showSuggestion(data)
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

// Hàm dùng khi chọn ô input sẽ tự động xuất hiện suggestion
function showAllSuggestions(input) {
    if (input === ''){
        fetch('/get-all-customer-suggestions')
        .then(response => response.json())
        .then(data => {
            showSuggestion(data);
        })
        .catch(error => {
            console.error('Error:', error);
        });
    } // Không có ký tự nào
    else {
        getSuggestions(input);
    }
}
// Thêm sự kiện nghe để bắt sự kiện click trên toàn bộ trang
document.addEventListener('click', function(event) {
    const suggestionsDiv = document.getElementById('suggestions');
    const input = document.getElementById('customer_id');

    // Kiểm tra xem sự kiện click có diễn ra trên ô input hoặc danh sách gợi ý không
    if (event.target !== input && event.target !== suggestionsDiv && !suggestionsDiv.contains(event.target)) {
        // Nếu không, ẩn danh sách gợi ý
        suggestionsDiv.style.display = 'none';
    }
});

// Sự kiện này để thay thế value của ô input thành customer_id, thay vì ô input trả về dữ liệu đuược nhập vào bởi người dùng
function getCustomerId(){
    document.getElementById('customer_id').value = ID;
}

// Thêm sự kiện để nghe checkbox
document.getElementById('is_odd_customer').addEventListener('change', function() {
    const formGroup = document.getElementById('new_customer_form');
    const existed_customer = document.getElementById('existed_customer')
    const newCustomerId = document.getElementById('new_customer_id');
    const newCustomerName = document.getElementById('new_customer_name');
    const newCustomerPhone = document.getElementById('new_customer_phone');
    const newCustomerTreatment = document.getElementById('new_customer_treatment')
    const price = document.getElementById('new_customer_treatment_price')
    const cardContainer = document.getElementById('customer-card-container');
    cardContainer.style.display = 'none'
    const customerID = document.getElementById('customer_id')
    if (this.checked) {
        formGroup.style.display = 'block';
        existed_customer.style.display = 'none';
        newCustomerId.setAttribute('required', 'required');
        newCustomerName.setAttribute('required', 'required');
        newCustomerPhone.setAttribute('required', 'required');
        price.setAttribute('required', 'required')
        customerID.removeAttribute('required');
    } else {
        formGroup.style.display = 'none';
        existed_customer.style.display = 'block';
        newCustomerId.removeAttribute('required');
        newCustomerName.removeAttribute('required');
        newCustomerPhone.removeAttribute('required');
        newCustomerTreatment.removeAttribute('required');
        price.removeAttribute('required')
        customerID.setAttribute('required', 'required');
    }
});