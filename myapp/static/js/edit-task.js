function toggleTaskDescription() {
    const taskOption = document.getElementById('description-option').value;
    const newTaskDiv = document.getElementById('new_task_div');

    if (taskOption === '1') {
        newTaskDiv.style.display = 'block';
    } else {
        newTaskDiv.style.display = 'none';
    }
}
document.addEventListener('DOMContentLoaded', function() {
    toggleTaskDescription();
});


function validateCheckboxes() {
    var finishedYes = document.getElementById('finished-yes');
    var finishedNo = document.getElementById('finished-no');

    if (!finishedYes.checked && !finishedNo.checked) {
        alert('Please select either Yes or No for the "Finished" field.');
        return false;
    }
    return true;
}