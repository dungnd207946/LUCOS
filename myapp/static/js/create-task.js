


// Hàm để chọn giữa 2 cách nhập nội dung task
function toggleTaskInput() {
    const taskOption = document.getElementById('existing_task').value;
    const newTaskDiv = document.getElementById('new_task_div');

    if (taskOption === '1') {
        newTaskDiv.style.display = 'block';
    } else {
        newTaskDiv.style.display = 'none';
    }
}


