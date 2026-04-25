document.addEventListener("DOMContentLoaded", () => {
    const selectors = [
        "main section",
        "main header",
        "main article",
        "main aside",
        "main form",
        "main footer",
        "main .grid > *",
        "main .flex > *",
        "main .glass-panel",
        "main .group",
        "main img"
    ];

    const elements = Array.from(new Set(
        selectors.flatMap((selector) => Array.from(document.querySelectorAll(selector)))
    )).filter((el) => {
        if (el.closest("header.fixed")) return false;
        if (el.id === "loader" || el.id === "custom-cursor" || el.id === "custom-cursor-follower") return false;
        const rect = el.getBoundingClientRect();
        return rect.width > 0 && rect.height > 0;
    });

    elements.forEach((el, index) => {
        el.classList.add("reveal-on-scroll");
        if (!el.dataset.reveal) {
            if (index % 5 === 1) el.dataset.reveal = "left";
            else if (index % 5 === 3) el.dataset.reveal = "right";
            else if (index % 5 === 4) el.dataset.reveal = "scale";
        }
        el.style.transitionDelay = `${Math.min(index * 45, 260)}ms`;
    });

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                entry.target.classList.add("is-visible");
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.12,
        rootMargin: "0px 0px -8% 0px"
    });

    elements.forEach((el) => observer.observe(el));
});
