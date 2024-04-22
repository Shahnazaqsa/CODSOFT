const body = document.querySelector('body'),
    leftbar = body.querySelector('.left-bar'),
    toggle = body.querySelector('.toggle'),
    searchbtn = body.querySelector('.search-box');

toggle.addEventListener("click", () => {
    leftbar.classList.toggle('close');
});

// alerts
function showAlert() {
    var alertBox = document.getElementById("myAlert");
    alertBox.style.display = "block";
}

function closeAlert(element) {
    var alertBox = element.closest('.alert');
    alertBox.style.display = 'none';
}

