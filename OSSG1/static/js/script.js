document.addEventListener("DOMContentLoaded", function () {
    // 自动隐藏消息框
    let alerts = document.querySelectorAll(".alert");
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = "0";
            setTimeout(() => alert.remove(), 500);
        }, 3000);
    });
});