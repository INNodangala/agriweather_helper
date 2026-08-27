/**
 * AgriWeather Helper - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Flash message close buttons
    const flashCloseButtons = document.querySelectorAll('.flash-close');
    flashCloseButtons.forEach(button => {
        button.addEventListener('click', function() {
            this.parentElement.remove();
        });
    });

    // Animate score bars on scroll
    animateScoreBars();

    // Register service worker for PWA
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/js/sw.js').catch(() => {});
    }
});

function animateScoreBars() {
    const scoreFills = document.querySelectorAll('.score-fill');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.width = entry.target.dataset.width || entry.target.style.width;
            }
        });
    }, { threshold: 0.5 });

    scoreFills.forEach(fill => {
        observer.observe(fill);
    });
}
