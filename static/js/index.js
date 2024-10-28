window.addEventListener('scroll', function() {
    const nav = document.querySelector('.navigation-container');
    
    if (window.scrollY > 0) {
        nav.classList.add('blurred');
    } else {
        nav.classList.remove('blurred');
    }
});
