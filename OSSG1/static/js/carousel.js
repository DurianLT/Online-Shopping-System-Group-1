document.addEventListener("DOMContentLoaded", function () {
    const carouselElement = document.querySelector("#carouselExample");
    const carousel = new bootstrap.Carousel(carouselElement);

    carouselElement.addEventListener("mouseenter", function () {
        carousel.pause(); // 鼠标悬停暂停轮播
    });

    carouselElement.addEventListener("mouseleave", function () {
        carousel.cycle(); // 鼠标移开恢复轮播
    });
});