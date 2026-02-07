const CATALOG_URL = "/data/themes.json";

export async function loadCatalog() {
  const response = await fetch(CATALOG_URL, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Failed to load catalog: ${response.status}`);
  }
  return response.json();
}

export function getThemeById(catalog, id) {
  if (!catalog || !Array.isArray(catalog.themes)) return null;
  return catalog.themes.find((item) => item.id === id) || null;
}

export function formatFileSize(sizeBytes) {
  if (!Number.isFinite(sizeBytes) || sizeBytes <= 0) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  let size = sizeBytes;
  let unitIndex = 0;
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex += 1;
  }
  const fixed = size < 10 && unitIndex > 0 ? 1 : 0;
  return `${size.toFixed(fixed)} ${units[unitIndex]}`;
}

export function formatDate(isoString) {
  if (!isoString) return "";
  const date = new Date(isoString);
  if (Number.isNaN(date.getTime())) return isoString;
  return new Intl.DateTimeFormat("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(date);
}

export function buildThemeUrl(themeId) {
  const url = new URL("/theme.html", window.location.origin);
  url.searchParams.set("id", themeId);
  return `${url.pathname}${url.search}`;
}

export function resolveSearch(items, keyword) {
  const query = (keyword || "").trim().toLowerCase();
  if (!query) return items;
  return items.filter((item) => {
    const fields = [
      item.name,
      item.author,
      item.description,
      item.id,
      ...(Array.isArray(item.tags) ? item.tags : []),
    ];
    return fields.some((field) => String(field || "").toLowerCase().includes(query));
  });
}

