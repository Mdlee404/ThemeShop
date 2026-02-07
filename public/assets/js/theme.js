const STORAGE_KEY = "theme-store-preference";

function systemPrefersDark() {
  return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
}

export function getSavedTheme() {
  try {
    const value = localStorage.getItem(STORAGE_KEY);
    if (value === "light" || value === "dark") return value;
  } catch (_error) {}
  return null;
}

export function currentTheme() {
  return document.documentElement.getAttribute("data-theme") || "light";
}

export function applyTheme(theme) {
  const next = theme === "dark" ? "dark" : "light";
  document.documentElement.setAttribute("data-theme", next);
  try {
    localStorage.setItem(STORAGE_KEY, next);
  } catch (_error) {}
  return next;
}

export function initTheme() {
  const selected = getSavedTheme() || (systemPrefersDark() ? "dark" : "light");
  document.documentElement.setAttribute("data-theme", selected);
  return selected;
}

export function toggleTheme() {
  return applyTheme(currentTheme() === "dark" ? "light" : "dark");
}

