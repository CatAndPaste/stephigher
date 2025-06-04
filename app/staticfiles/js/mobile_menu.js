document.addEventListener('DOMContentLoaded', function () {
    const burger = document.querySelector('.header__burger');
    const mobileMenu = document.querySelector('.header__mobile-menu');

    burger.addEventListener('click', function () {
        this.classList.toggle('active');
        mobileMenu.classList.toggle('active');

        // Анимация бургер-иконки в крестик
        const lines = this.querySelectorAll('.header__burger-line');
        if (this.classList.contains('active')) {
            lines[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
            lines[1].style.opacity = '0';
            lines[2].style.transform = 'rotate(-45deg) translate(6px, -8px)';
        } else {
            lines.forEach(line => {
                line.style.transform = '';
                line.style.opacity = '';
            });
        }
    });
});