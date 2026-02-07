const ICONS = {
  logo: `
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <defs>
        <linearGradient id="g-logo" x1="0" y1="0" x2="24" y2="24" gradientUnits="userSpaceOnUse">
          <stop offset="0" stop-color="#7c3aed"></stop>
          <stop offset="1" stop-color="#06b6d4"></stop>
        </linearGradient>
      </defs>
      <path d="M12 2l8 4.4v11.2L12 22l-8-4.4V6.4L12 2z" stroke="url(#g-logo)" stroke-width="1.5"></path>
      <path d="M8 11.2l2.6 2.6L16 8.3" stroke="url(#g-logo)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"></path>
    </svg>
  `,
  sun: `
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="4" stroke="currentColor" stroke-width="1.6"></circle>
      <path d="M12 2v2.2M12 19.8V22M4.9 4.9l1.6 1.6M17.5 17.5l1.6 1.6M2 12h2.2M19.8 12H22M4.9 19.1l1.6-1.6M17.5 6.5l1.6-1.6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"></path>
    </svg>
  `,
  moon: `
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M20 14.3A8.3 8.3 0 1 1 9.7 4a7.2 7.2 0 1 0 10.4 10.3z" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"></path>
    </svg>
  `,
  search: `
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="11" cy="11" r="6" stroke="currentColor" stroke-width="1.6"></circle>
      <path d="M20 20l-4.2-4.2" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"></path>
    </svg>
  `,
  author: `
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="8" r="3.2" stroke="currentColor" stroke-width="1.6"></circle>
      <path d="M5 19a7 7 0 0 1 14 0" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"></path>
    </svg>
  `,
  info: `
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.6"></circle>
      <path d="M12 10.2v6.2" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"></path>
      <circle cx="12" cy="7.2" r=".9" fill="currentColor"></circle>
    </svg>
  `,
  download: `
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M12 3v11" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"></path>
      <path d="M7.6 9.6L12 14l4.4-4.4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"></path>
      <path d="M4 19.2h16" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"></path>
    </svg>
  `,
  arrowRight: `
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M5 12h14" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"></path>
      <path d="M13.5 6.8L19 12l-5.5 5.2" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"></path>
    </svg>
  `,
  arrowLeft: `
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M19 12H5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"></path>
      <path d="M10.5 6.8L5 12l5.5 5.2" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"></path>
    </svg>
  `,
  palette: `
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M12 4a8 8 0 0 0 0 16h1.1a2.2 2.2 0 0 0 2.2-2.2c0-1 .7-1.8 1.7-1.8h1.4A3.6 3.6 0 0 0 22 12a8 8 0 0 0-10-8z" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"></path>
      <circle cx="7.8" cy="10" r="1" fill="currentColor"></circle>
      <circle cx="10.8" cy="7.7" r="1" fill="currentColor"></circle>
      <circle cx="14.3" cy="7.8" r="1" fill="currentColor"></circle>
      <circle cx="16.7" cy="10.8" r="1" fill="currentColor"></circle>
    </svg>
  `,
  spark: `
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M12 3.4l1.8 4.6L18.4 10l-4.6 1.8L12 16.4l-1.8-4.6L5.6 10l4.6-2z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"></path>
      <path d="M18.7 4.6l.7 1.7 1.7.7-1.7.7-.7 1.7-.7-1.7-1.7-.7 1.7-.7zM5.3 14.7l.7 1.7 1.7.7-1.7.7-.7 1.7-.7-1.7-1.7-.7 1.7-.7z" fill="currentColor"></path>
    </svg>
  `,
  phone: `
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <rect x="7" y="2.8" width="10" height="18.4" rx="2" stroke="currentColor" stroke-width="1.6"></rect>
      <path d="M10 5.6h4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"></path>
      <circle cx="12" cy="18.2" r=".9" fill="currentColor"></circle>
    </svg>
  `,
  desktop: `
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <rect x="3" y="4.5" width="18" height="12" rx="2" stroke="currentColor" stroke-width="1.6"></rect>
      <path d="M9 20h6M12 16.5V20" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"></path>
    </svg>
  `,
  code: `
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <path d="M8 8.4L4.4 12 8 15.6M16 8.4l3.6 3.6-3.6 3.6M13.5 6l-3 12" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"></path>
    </svg>
  `,
  check: `
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.6"></circle>
      <path d="M8.5 12.2l2.4 2.4 4.8-4.8" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"></path>
    </svg>
  `,
  copy: `
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <rect x="8" y="8" width="10" height="12" rx="1.8" stroke="currentColor" stroke-width="1.6"></rect>
      <path d="M6 15H5a1 1 0 0 1-1-1V5.8A1.8 1.8 0 0 1 5.8 4H14a1 1 0 0 1 1 1v1" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"></path>
    </svg>
  `,
};

export function icon(name, className = "") {
  const raw = ICONS[name] || "";
  if (!raw) return "";
  if (!className) return raw;
  return raw.replace("<svg ", `<svg class="${className}" `);
}

export function setIcon(element, name, className = "") {
  if (!element) return;
  element.innerHTML = icon(name, className);
}

