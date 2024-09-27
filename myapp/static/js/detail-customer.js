function delete_customer(id){ // button delete
    check = confirm("Bạn chắc chắn muốn xóa khách hàng này ?");
    if(check){
        var api = '/khach-hang/infor-khach-hang/delete/' + id;
        fetch(api, {
            method: 'DELETE'
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }

                return response.json();
        })
        .then(data => {
            alert('Xóa khách hàng thành công!');
            window.location.href = "/khach-hang/infor-khach-hang"
        })
        .catch((error) => console.error('Error:', error));

    }
}

function redirectToProduct(url) {
    // Kiểm tra xem url có tồn tại không
    if (url === "None") {
        window.location.href = "#"; // Nếu tồn tại, chuyển hướng đến URL
    } else {
        window.location.href = url; // Nếu không tồn tại, chuyển hướng đến '#'
    }
}