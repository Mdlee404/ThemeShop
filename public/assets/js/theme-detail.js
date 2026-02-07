import { icon, setIcon } from "./icons.js";
import {
  loadCatalog,
  getThemeById,
  formatDate,
  formatFileSize,
} from "./catalog.js";
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
  const dark = currentTheme() === "dark";
  button.setAttribute("aria-label", dark ? "切换为日间模式" : "切换为夜间模式");
  button.innerHTML = dark ? icon("sun", "icon") : icon("moon", "icon");
}

function getQueryId() {
  const params = new URLSearchParams(window.location.search);
  return (params.get("id") || "").trim().toLowerCase();
}

function renderGallery(theme) {
  const gallery = Array.isArray(theme.paths?.gallery) ? theme.paths.gallery : [];
  const fallback = theme.paths?.preview || "";
  const images = gallery.length ? gallery : fallback ? [fallback] : [];

  const main = byId("detailMainImage");
  const thumbs = byId("detailThumbs");

  if (!images.length) {
    main.alt = `${theme.name} 暂无预览图`;
    main.src = "";
    main.style.display = "none";
    thumbs.innerHTML = `<div class="hint">暂无预览图</div>`;
    return;
  }

  main.style.display = "block";
  main.src = images[0];
  main.alt = `${theme.name} 预览图`;

  thumbs.innerHTML = images
    .map(
      (url, index) => `
      <button class="thumb-btn ${index === 0 ? "active" : ""}" type="button" data-url="${url}" aria-label="查看第 ${index + 1} 张预览">
        <img src="${url}" alt="${theme.name} 缩略图 ${index + 1}" loading="lazy" decoding="async" />
      </button>
    `,
    )
    .join("");

  thumbs.querySelectorAll(".thumb-btn").forEach((button) => {
    button.addEventListener("click", () => {
      const url = button.getAttribute("data-url") || "";
      if (!url) return;
      main.src = url;
      thumbs.querySelectorAll(".thumb-btn").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
    });
  });
}

function renderMeta(theme) {
  byId("themeName").textContent = theme.name || theme.id;
  byId("themeDescription").textContent = theme.description || "暂无描述";
  byId("themeAuthor").textContent = theme.author || "未知作者";
  byId("themeVersion").textContent = theme.version || "1.0.0";
  byId("themeSchema").textContent = theme.schemaVersion || "1.0";
  byId("themeAppMin").textContent = theme.minAppVersion || "1.0.0";
  byId("themePlatformMin").textContent = String(theme.minPlatformVersion || "1000");
  byId("themeUpdated").textContent = formatDate(theme.updatedAt) || "--";

  const fileName = theme.package?.fileName || "theme.zip";
  const fileSize = formatFileSize(theme.package?.sizeBytes || 0);
  byId("themePackage").textContent = `${fileName} (${fileSize})`;

  const tags = Array.isArray(theme.tags) ? theme.tags : [];
  byId("themeTags").innerHTML = tags.length ? tags.map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`).join("") : '<span class="hint">暂无标签</span>';

  const downloadButton = byId("downloadBtn");
  const downloadUrl = theme.package?.downloadUrl || "#";
  downloadButton.href = downloadUrl;
  downloadButton.setAttribute("download", fileName);

  const rawJsonUrl = theme.paths?.themeJson || "";
  const rawJsonButton = byId("rawJsonBtn");
  rawJsonButton.href = rawJsonUrl;
  rawJsonButton.target = "_blank";
  rawJsonButton.rel = "noreferrer";
}

function bindCopyButton(theme) {
  const button = byId("copySnippetBtn");
  const snippet = {
    id: theme.id,
    name: theme.name,
    author: theme.author,
    description: theme.description,
    package: theme.package,
    preview: theme.paths?.preview,
  };

  button.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(snippet, null, 2));
      button.textContent = "已复制";
      setTimeout(() => {
        button.innerHTML = `${icon("copy", "icon")} 复制主题片段`;
      }, 1200);
    } catch (_error) {
      button.textContent = "复制失败";
    }
  });
}

async function renderRawThemeJson(theme) {
  const code = byId("rawThemeJson");
  code.textContent = "加载中...";

  if (!theme.paths?.themeJson) {
    code.textContent = "未找到 theme.json";
    return;
  }

  try {
    const response = await fetch(theme.paths.themeJson, { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    code.textContent = JSON.stringify(data, null, 2);
  } catch (error) {
    code.textContent = `读取失败: ${error.message}`;
  }
}

async function bootstrap() {
  initTheme();
  setIcon(byId("logoIcon"), "logo", "brand-icon");
  setIcon(byId("backIcon"), "arrowLeft", "icon");
  setIcon(byId("downloadIcon"), "download", "icon");
  setIcon(byId("copyIcon"), "copy", "icon");

  const themeSwitch = byId("themeSwitch");
  renderThemeButton(themeSwitch);
  themeSwitch.addEventListener("click", () => {
    toggleTheme();
    renderThemeButton(themeSwitch);
  });

  const loading = byId("loadingState");
  const errorState = byId("errorState");
  const queryId = getQueryId();

  if (!queryId) {
    loading.hidden = true;
    errorState.hidden = false;
    byId("errorMessage").textContent = "缺少主题 id 参数";
    return;
  }

  try {
    const catalog = await loadCatalog();
    const theme = getThemeById(catalog, queryId);
    if (!theme) {
      throw new Error(`未找到主题：${queryId}`);
    }

    document.title = `${theme.name} · 主题详情`;
    renderMeta(theme);
    renderGallery(theme);
    bindCopyButton(theme);
    await renderRawThemeJson(theme);

    loading.hidden = true;
  } catch (error) {
    loading.hidden = true;
    errorState.hidden = false;
    byId("errorMessage").textContent = error.message;
  }
}

bootstrap();
