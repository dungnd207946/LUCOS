function confirmLogout(){
    check = confirm("Bạn chắc chắn muốn đăng xuất ?");
    if(check){
        alert('Đăng xuất thành công!');
        window.location.href = '/logout';
    }
}