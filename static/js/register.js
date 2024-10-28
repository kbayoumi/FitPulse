document.addEventListener('DOMContentLoaded', function () {
    const togglePassword = document.getElementById('togglePassword');
    const passwordField = document.getElementById('password');

    togglePassword.addEventListener('click', function () {
        const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordField.setAttribute('type', type);
        this.querySelector('i').classList.toggle('fa-eye-slash');
    });
});


let currentSection = 0;
const sections = document.querySelectorAll('.wrapper, .wrapper1, .wrapper2, .wrapper3,.wrapper4');

function showNextSection() {
    if (currentSection < sections.length - 1) {
        sections[currentSection].style.display = 'none';
        currentSection++;
        sections[currentSection].style.display = 'block';
    }
}

function showPrevSection() {
    if (currentSection > 0) {
        sections[currentSection].style.display = 'none';
        currentSection--;
        sections[currentSection].style.display = 'block';
    }
}

// Initialize first section
sections[currentSection].style.display = 'block';
