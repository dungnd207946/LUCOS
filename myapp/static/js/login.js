
function loginSuccess(){
    //window.location.href = '/khach-hang';
    window.location.href = '/khach-hang';
}
function thong_bao_login(){
    window.parent.loginSuccess();
}
// Đây là cách lấy dữ liệu từ server ra rồi xử lí ở front-end
document.getElementById('login-form').addEventListener('submit', function(event) {
  event.preventDefault(); // Ngăn chặn hành vi gửi form mặc định

  // Lấy giá trị từ form
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  console.log(username)
  console.log(password)
  // Gọi hàm để so sánh với API
  compareWithApi(username, password);
});

function compareWithApi(username, password) {
  // Đường dẫn API của bạn
  const apiURL = '/get_user';

  // Sử dụng Fetch API để lấy dữ liệu người dùng
  fetch(apiURL)
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(users => {
      // So sánh email và password với dữ liệu nhận được từ API
      const user = users.find(user => user.user_password === password && user.username === username);
      if (user) {
          alert('Đăng nhập thành công!');
          thong_bao_login();
      } else {
        alert('Username hoặc mật khẩu không đúng.');
        window.location.reload();
      }
    })
    .catch(error => console.error('There was a problem with your fetch operation:', error));
}
