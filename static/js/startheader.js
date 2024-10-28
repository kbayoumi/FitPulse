document.addEventListener('DOMContentLoaded', () => {
    const loginContainer = document.querySelector('.login-container');
    const dropdownMenu = loginContainer.querySelector('.dropdown-menu');

    loginContainer.addEventListener('click', () => {
        dropdownMenu.style.display = dropdownMenu.style.display === 'block' ? 'none' : 'block';
    });

    // Close dropdown if clicked outside
    document.addEventListener('click', (event) => {
        if (!loginContainer.contains(event.target)) {
            dropdownMenu.style.display = 'none';
        }
    });
});

