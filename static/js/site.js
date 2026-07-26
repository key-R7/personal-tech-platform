(() => {
    "use strict";

    const showcases = Array.from(
        document.querySelectorAll("[data-split-showcase]")
    );
    if (!showcases.length) {
        return;
    }

    const reducedMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)"
    );
    const desktopLayout = window.matchMedia("(min-width: 768px)");
    let frameRequested = false;

    function setStaticState(showcase) {
        showcase.style.setProperty("--split-gap", "24px");
        showcase.style.setProperty("--split-cover-opacity", "0");
        showcase.style.setProperty("--split-content-opacity", "1");
        showcase.style.setProperty("--split-left-rotate", "-7deg");
        showcase.style.setProperty("--split-right-rotate", "7deg");
        showcase.style.setProperty("--split-left-shift", "-10px");
        showcase.style.setProperty("--split-right-shift", "10px");
        showcase.style.setProperty("--split-center-lift", "-18px");
    }

    function updateShowcases() {
        frameRequested = false;

        if (reducedMotion.matches || !desktopLayout.matches) {
            showcases.forEach(setStaticState);
            return;
        }

        const viewportHeight = window.innerHeight;
        const animationStart = viewportHeight * 0.86;
        const animationEnd = viewportHeight * 0.28;
        const distance = animationStart - animationEnd;

        showcases.forEach((showcase) => {
            const rect = showcase.getBoundingClientRect();
            const progress = Math.min(
                1,
                Math.max(0, (animationStart - rect.top) / distance)
            );
            const eased = 1 - Math.pow(1 - progress, 3);

            showcase.style.setProperty(
                "--split-gap",
                `${Math.round(eased * 28)}px`
            );
            showcase.style.setProperty(
                "--split-cover-opacity",
                `${Math.max(0, 1 - eased * 1.45)}`
            );
            showcase.style.setProperty(
                "--split-content-opacity",
                `${Math.max(0, (eased - 0.18) / 0.82)}`
            );
            showcase.style.setProperty(
                "--split-left-rotate",
                `${-8 * eased}deg`
            );
            showcase.style.setProperty(
                "--split-right-rotate",
                `${8 * eased}deg`
            );
            showcase.style.setProperty(
                "--split-left-shift",
                `${-14 * eased}px`
            );
            showcase.style.setProperty(
                "--split-right-shift",
                `${14 * eased}px`
            );
            showcase.style.setProperty(
                "--split-center-lift",
                `${-24 * eased}px`
            );
        });
    }

    function requestUpdate() {
        if (!frameRequested) {
            frameRequested = true;
            window.requestAnimationFrame(updateShowcases);
        }
    }

    const listenForMediaChange = (mediaQuery) => {
        if (typeof mediaQuery.addEventListener === "function") {
            mediaQuery.addEventListener("change", requestUpdate);
            return;
        }

        mediaQuery.addListener(requestUpdate);
    };

    window.addEventListener("scroll", requestUpdate, { passive: true });
    window.addEventListener("resize", requestUpdate);
    listenForMediaChange(reducedMotion);
    listenForMediaChange(desktopLayout);
    updateShowcases();
})();
