import { icon, setIcon } from "./icons.js";
import { loadCatalog, resolveSearch, buildThemeUrl, formatDate } from "./catalog.js";
import { initTheme, currentTheme, toggleTheme } from "./theme.js";

function byId(id) {
  return document.getElementById(id);
}

function escapeHtml(raw) {
  return String(raw || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function renderThemeButton(button) {
  if (!button) return;
  const dark = currentTheme() === "dark";
  button.setAttribute("aria-label", dark ? "切换为日间模式" : "切换为夜间模式");
  button.innerHTML = dark ? icon("sun", "icon") : icon("moon", "icon");
}

function renderStats(catalog) {
  const count = catalog.count || 0;
  const generatedAt = catalog.generatedAt || "";
  const warnings = Array.isArray(catalog.warnings) ? catalog.warnings.length : 0;

  byId("statCount").textContent = String(count);
  byId("statDate").textContent = generatedAt ? formatDate(generatedAt) : "--";
  byId("statWarnings").textContent = String(warnings);
}

function renderCard(theme) {
  const tags = Array.isArray(theme.tags) ? theme.tags : [];
  const preview = theme.paths?.preview || "";
  const safeName = escapeHtml(theme.name);
  const safeDescription = escapeHtml(theme.description || "暂无描述");
  const safeAuthor = escapeHtml(theme.author || "未知作者");
  const safeVersion = escapeHtml(theme.version || "1.0.0");
  const safeTags = tags.slice(0, 3).map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`).join("");

  return `
    <article class="theme-card glass-card" data-theme-id="${theme.id}">
      <a class="theme-preview-link" href="${buildThemeUrl(theme.id)}" aria-label="查看 ${safeName} 详情">
        <div class="theme-preview-wrap">
          ${preview ? `<img src="${preview}" alt="${safeName} 预览图" loading="lazy" decoding="async" class="theme-preview">` : `<div class="theme-preview fallback">${icon("palette", "icon")}</div>`}
          <div class="preview-overlay">
            <span class="chip">${icon("spark", "icon")} 查看详情</span>
          </div>
        </div>
      </a>
      <div class="theme-content">
        <h3 class="theme-title">${safeName}</h3>
        <p class="theme-description">${safeDescription}</p>
        <div class="meta-row">
          <span class="meta-item">${icon("author", "icon")} ${safeAuthor}</span>
          <span class="meta-item">v${safeVersion}</span>
        </div>
        <div class="meta-tags">
          ${safeTags}
        </div>
        <div class="card-actions">
          <a class="btn ghost" href="${buildThemeUrl(theme.id)}">查看详情 ${icon("arrowRight", "icon")}</a>
        </div>
      </div>
    </article>
  `;
}

function renderGrid(items) {
  const grid = byId("themeGrid");
  const empty = byId("emptyState");
  if (!items.length) {
    grid.innerHTML = "";
    empty.hidden = false;
    return;
  }
  empty.hidden = true;
  grid.innerHTML = items.map(renderCard).join("");
}

function bindIcons() {
  setIcon(byId("logoIcon"), "logo", "brand-icon");
  setIcon(byId("searchIcon"), "search", "icon");
  setIcon(byId("heroSpark"), "spark", "icon");
  setIcon(byId("featureMobile"), "phone", "icon");
  setIcon(byId("featureDesktop"), "desktop", "icon");
  setIcon(byId("featureCode"), "code", "icon");
}

function bindThemeToggle() {
  const button = byId("themeSwitch");
  renderThemeButton(button);
  button.addEventListener("click", () => {
    toggleTheme();
    renderThemeButton(button);
  });
}

async function bootstrap() {
  initTheme();
  bindIcons();
  bindThemeToggle();

  const loading = byId("loadingState");
  const errorState = byId("errorState");
  const searchInput = byId("searchInput");

  try {
    const catalog = await loadCatalog();
    const themes = Array.isArray(catalog.themes) ? catalog.themes : [];

    renderStats(catalog);
    renderGrid(themes);

    searchInput.addEventListener("input", () => {
      const filtered = resolveSearch(themes, searchInput.value);
      renderGrid(filtered);
    });

    loading.hidden = true;
  } catch (error) {
    loading.hidden = true;
    errorState.hidden = false;
    byId("errorMessage").textContent = error.message;
  }
}

bootstrap();
