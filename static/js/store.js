
document.addEventListener('DOMContentLoaded', () => {
    const leftArrow = document.querySelector('.left-arrow');
    const rightArrow = document.querySelector('.right-arrow');
    const carouselContent = document.querySelector('.carousel-content');
    const slides = document.querySelectorAll('.slide');
    const slideWidth = slides[0].offsetWidth; // Get the width of a single slide

    let currentIndex = 0;

    function updateSlides() {
        const offset = -currentIndex * slideWidth; // Move to the current slide
        carouselContent.style.transform = `translateX(${offset}px)`;
    }

    leftArrow.addEventListener('click', () => {
        if (currentIndex > 0) {
            currentIndex--;
            updateSlides();
        }
    });

    rightArrow.addEventListener('click', () => {
        if (currentIndex < slides.length - 1) {
            currentIndex++;
            updateSlides();
        }
    });

    // Initialize the carousel position
    updateSlides();
});

document.addEventListener('DOMContentLoaded', function () {
    const slider = document.querySelector('.image-slider');
    const images = document.querySelectorAll('.image-slider img');
    let currentIndex = 0;
    const totalImages = images.length;
    
    // Function to move to the next slide
    function slideToNextImage() {
        currentIndex = (currentIndex + 1) % totalImages; // Loop back to the first image
        const offset = -currentIndex * 100; // Calculate the offset for the transform
        slider.style.transform = `translateX(${offset}%)`;
    }
    
    // Slide every 3 seconds
    setInterval(slideToNextImage, 3000);
});



document.addEventListener('DOMContentLoaded', () => {
    const leftArrow2 = document.querySelector('.left-arrow3');
    const rightArrow2 = document.querySelector('.right-arrow3');
    const carouselContent2 = document.querySelector('.carousel-content3');
    const slides2 = document.querySelectorAll('.slide3');
    const slideWidth2 = slides2[0].offsetWidth; // Get the width of a single slide

    let currentIndex2 = 0;

    function updateSlides2() {
        const offset2 = -currentIndex2 * slideWidth2; // Move to the current slide
        carouselContent2.style.transform = `translateX(${offset2}px)`;
    }

    leftArrow2.addEventListener('click', () => {
        if (currentIndex2 > 0) {
            currentIndex2--;
            updateSlides2();
        }
    });

    rightArrow2.addEventListener('click', () => {
        if (currentIndex2 < slides2.length - 1) {
            currentIndex2++;
            updateSlides2();
        }
    });

    // Initialize the carousel position
    updateSlides2();
});