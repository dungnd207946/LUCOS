function previewImage() {
    const file = document.getElementById('profile_image').files[0];
    const preview = document.getElementById('image-preview');
    const cameraIcon = document.querySelector('.camera-icon');
    const chooseFileText = document.querySelector('.choose-file-text');

    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.style.display = 'block'; // Hiện ảnh preview
            // cameraIcon.style.display = 'none'; // Ẩn icon máy ảnh
            // chooseFileText.style.display = 'none'; // Ẩn chữ "Chọn tệp"
        }
        reader.readAsDataURL(file);
    }
    else {
        preview.src = '';
        preview.style.display = 'none'; // Ẩn ảnh preview
        // cameraIcon.style.display = 'block'; // Hiện icon máy ảnh
        // chooseFileText.style.display = 'block'; // Hiện chữ "Chọn tệp"
    }
}

