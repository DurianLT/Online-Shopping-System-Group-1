let currentIndex = 0;
const carouselItems = document.querySelectorAll('.carousel-item');
const totalItems = carouselItems.length;

function changeImage() {
    currentIndex = (currentIndex + 1) % totalItems;
    document.querySelector('.carousel-images').style.transform = `translateX(-${currentIndex * 100}%)`;
}

// 每5秒切换一次图片
setInterval(changeImage, 5000);
