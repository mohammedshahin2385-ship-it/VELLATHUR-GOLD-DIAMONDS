document.addEventListener("DOMContentLoaded", () => {
    const header = document.querySelector("header.fixed");
    if (!header) return;

    const headerBar = header.firstElementChild;
    if (!headerBar) return;

    header.classList.add("kia-header-shell");
    headerBar.classList.add("kia-header-bar");

    const logoImage = header.querySelector("img");
    if (logoImage) {
        logoImage.classList.add("kia-header-logo-mark");
    }

    const logoText = header.querySelector("a.flex.flex-col span");
    if (logoText) {
        logoText.classList.add("kia-header-logo-text");
    }

    const logoAccent = header.querySelector("a.flex.flex-col span + span");
    if (logoAccent) {
        logoAccent.classList.add("kia-header-logo-accent");
    }

    const currentPage = window.location.pathname.split("/").pop() || "home.html";
    const navLinks = header.querySelectorAll("nav a");
    navLinks.forEach((link) => {
        link.classList.add("kia-nav-link");
        const href = link.getAttribute("href");
        const isCurrent = link.className.includes("border-b-2") || (href && href !== "#" && href === currentPage);
        if (isCurrent) {
            link.classList.add("kia-nav-current");
        }
    });

    const metaNodes = header.querySelectorAll(".text-\\[\\#CCA365\\], .text-\\[\\#F5F2EB\\]");
    metaNodes.forEach((node) => {
        if (!node.closest("nav") && !node.closest("a.flex.flex-col")) {
            node.classList.add("kia-header-meta");
        }
    });

    const syncHeaderState = () => {
        header.classList.toggle("kia-header-scrolled", window.scrollY > 24);
    };

    const headerRateSummary = document.getElementById("header-rate-summary");
    const formatCurrency = (value) => `\u20B9${Number(value).toLocaleString("en-IN")}`;
    const loadHeaderRate = async () => {
        if (!headerRateSummary) return;
        try {
            const response = await fetch("/api/rates");
            if (!response.ok) return;
            const payload = await response.json();
            const rates = payload && payload.rates ? payload.rates : null;
            if (!rates || rates.rate_22k_1g == null) return;
            headerRateSummary.textContent = `22K: ${formatCurrency(rates.rate_22k_1g)}/gm`;
        } catch {
            // Keep existing static text if API is unavailable.
        }
    };

    syncHeaderState();
    window.addEventListener("scroll", syncHeaderState, { passive: true });
    loadHeaderRate();
});
