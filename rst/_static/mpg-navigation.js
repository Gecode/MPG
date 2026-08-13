(() => {
  const dialog = document.getElementById("mpg-mobile-navigation");
  const openButton = document.querySelector("[data-mpg-dialog-open='mpg-mobile-navigation']");
  if (!(dialog instanceof HTMLDialogElement) || !(openButton instanceof HTMLButtonElement)) return;

  openButton.addEventListener("click", () => {
    if (!dialog.open) dialog.showModal();
  });

  const storagePrefix = "mpg-navigation-open:";
  document.querySelectorAll(".mpg-nav-group[data-nav-key]").forEach((group) => {
    const key = storagePrefix + group.dataset.navKey;
    try {
      if (localStorage.getItem(key) === "true") group.open = true;
    } catch (_) {
      // Navigation remains fully usable when storage is unavailable.
    }
    group.addEventListener("toggle", () => {
      try { localStorage.setItem(key, String(group.open)); } catch (_) {}
    });
  });

  const initializeSectionTracking = (root) => {
    const sectionLinks = [...root.querySelectorAll('.mpg-section-navigation a[href^="#"]')];
    const sections = sectionLinks.map((link) => {
      const id = decodeURIComponent(link.hash.slice(1));
      return { link, section: document.getElementById(id) };
    }).filter(({ section }) => section);
    if (!sections.length) return;

    const navigationScroller = root.querySelector(".mpg-navigation-scroll");
    let currentSection = null;
    let scheduled = false;
    const updateSection = () => {
      scheduled = false;
      let current = sections[0];
      for (const candidate of sections) {
        if (candidate.section.getBoundingClientRect().top <= 140) current = candidate;
      }
      for (const candidate of sections) {
        if (candidate === current) candidate.link.setAttribute("aria-current", "location");
        else candidate.link.removeAttribute("aria-current");
      }
      if (current !== currentSection && navigationScroller) {
        current.link.scrollIntoView({ block: "nearest" });
      }
      currentSection = current;
    };
    const scheduleUpdate = () => {
      if (!scheduled) {
        scheduled = true;
        requestAnimationFrame(updateSection);
      }
    };
    addEventListener("scroll", scheduleUpdate, { passive: true });
    addEventListener("hashchange", scheduleUpdate);
    updateSection();
  };

  document.querySelectorAll(".mpg-sidebar, .mpg-mobile-navigation-panel")
    .forEach(initializeSectionTracking);
})();
