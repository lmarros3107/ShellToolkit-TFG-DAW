document.addEventListener("DOMContentLoaded", function () {
    var currentPath = window.location.pathname;
    var navLinks = document.querySelectorAll(".nav-links a");

    navLinks.forEach(function (link) {
        var href = link.getAttribute("href");
        if (href && href !== "/" && currentPath.startsWith(href)) {
            link.classList.add("active");
        }
        if (href === "/" && currentPath === "/") {
            link.classList.add("active");
        }
    });
});

