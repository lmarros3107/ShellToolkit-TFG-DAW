document.addEventListener("click", function (event) {
    var button = event.target.closest("[data-copy-target]");
    if (!button) {
        return;
    }

    var selector = button.getAttribute("data-copy-target");
    var target = document.querySelector(selector);
    if (!target) {
        return;
    }

    var textToCopy = target.innerText || target.textContent || "";
    navigator.clipboard.writeText(textToCopy).then(function () {
        var original = button.innerText;
        button.innerText = "Copied";
        window.setTimeout(function () {
            button.innerText = original;
        }, 1200);
    });
});

