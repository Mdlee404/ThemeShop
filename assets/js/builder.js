import { icon, setIcon } from "./icons.js";
import { initTheme, currentTheme, toggleTheme } from "./theme.js";
import { buildZip } from "./zip.js";

const DEFAULT_THEME = {
  schemaVersion: "1.0",
  id: "my_theme",
  name: "我的主题",
  version: "1.0.0",
  author: "",
  description: "",
  minAppVersion: "1.0.0",
  minPlatformVersion: 1000,
  colors: {
    theme: "#00E5FF",
    background: "#0D1221",
    text_primary: "rgba(255,244,220,0.92)",
    text_secondary: "rgba(255,244,220,0.65)",
    slider_selected: "#00E5FF",
    slider_block: "#00E5FF",
    slider_unselected: "rgba(255,244,220,0.2)",
  },
  text: {
    title: "rgba(255,244,220,0.92)",
    body: "rgba(255,244,220,0.82)",
    caption: "rgba(255,244,220,0.6)",
    danger: "#E35A5A",
  },
  lyric: {
    active: "#00E5FF",
    normal: "#FFF2D9",
    active_bg: "rgba(0,229,255,0.25)",
  },
  icons: {
    dark_mode: false,
    path: "icons",
  },
  backgrounds: {
    app: { type: "color", value: "#0D1221" },
    card: { type: "color", value: "rgba(13,18,33,0.55)" },
  },
  buttons: {
    primary: {
      bg: "rgba(0,229,255,0.18)",
      text: "#E6FCFF",
      border: "rgba(0,229,255,0.4)",
      image: "buttons/primary.png",
    },
    danger: {
      bg: "rgba(227,90,90,0.2)",
      text: "#E35A5A",
      border: "rgba(227,90,90,0.4)",
      image: "buttons/danger.png",
    },
  },
  assets: {
    base: ".",
    images: "images",
    buttons: "buttons",
  },
};

function byId(id) {
  return document.getElementById(id);
}

function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

function rgbaToHex(value, fallback = "#ffffff") {
  if (!value) return fallback;
  if (value.startsWith("#")) return value;
  const match = value.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/i);
  if (!match) return fallback;
  const [r, g, b] = [Number(match[1]), Number(match[2]), Number(match[3])].map((n) => Math.max(0, Math.min(255, n)));
  return `#${[r, g, b]
    .map((n) => n.toString(16).padStart(2, "0"))
    .join("")}`;
}

function safeId(value) {
  return String(value || "")
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9_]+/g, "_")
    .replace(/^_+|_+$/g, "") || "my_theme";
}

function renderThemeToggle(button) {
  const dark = currentTheme() === "dark";
  button.innerHTML = dark ? icon("sun", "icon") : icon("moon", "icon");
  button.setAttribute("aria-label", dark ? "切换为日间模式" : "切换为夜间模式");
}

function prettyJson(data) {
  return JSON.stringify(data, null, 2);
}

function bindInput(id, handler) {
  const node = byId(id);
  node.addEventListener("input", () => handler(node.value));
  return node;
}

function setMockTheme(theme) {
  const screen = byId("mockScreen");
  const colors = theme.colors;
  const buttons = theme.buttons || {};
  const primary = buttons.primary || {};
  const danger = buttons.danger || {};

  screen.style.background = colors.background || "#0D1221";
  screen.style.color = colors.text_primary || "#fff";

  byId("mockTitle").style.color = theme.text?.title || colors.text_primary;
  byId("mockBody").style.color = theme.text?.body || colors.text_secondary;
  byId("mockSub").style.color = theme.text?.caption || colors.text_secondary;

  const primaryBtn = byId("mockPrimary");
  primaryBtn.style.background = primary.bg || "rgba(0,229,255,0.18)";
  primaryBtn.style.color = primary.text || "#fff";
  primaryBtn.style.borderColor = primary.border || "transparent";

  const dangerBtn = byId("mockDanger");
  dangerBtn.style.background = danger.bg || "rgba(227,90,90,0.2)";
  dangerBtn.style.color = danger.text || "#f87171";
  dangerBtn.style.borderColor = danger.border || "transparent";

  byId("mockLyric").style.color = theme.lyric?.active || colors.theme;
  byId("mockProgress").style.background = colors.slider_unselected || "rgba(255,255,255,0.2)";
  byId("mockProgressInner").style.background = colors.slider_selected || colors.theme;
}

function createBuilderState() {
  return clone(DEFAULT_THEME);
}

function setupBuilder() {
  const state = createBuilderState();
  const assets = {
    preview: null,
    bgApp: null,
    primaryBtn: null,
    dangerBtn: null,
  };

  const applyJsonView = () => {
    byId("jsonPreview").textContent = prettyJson(state);
    setMockTheme(state);
  };

  const setField = (path, value) => {
    const keys = path.split(".");
    let ref = state;
    for (let i = 0; i < keys.length - 1; i += 1) ref = ref[keys[i]];
    ref[keys[keys.length - 1]] = value;
    applyJsonView();
  };

  bindInput("themeId", (value) => {
    const next = safeId(value);
    if (next !== value) byId("themeId").value = next;
    setField("id", next);
  });
  bindInput("themeName", (value) => setField("name", value || "我的主题"));
  bindInput("themeVersion", (value) => setField("version", value || "1.0.0"));
  bindInput("themeAuthor", (value) => setField("author", value));
  bindInput("themeDesc", (value) => setField("description", value));
  bindInput("themeMinApp", (value) => setField("minAppVersion", value || "1.0.0"));
  bindInput("themeMinPlatform", (value) => {
    const n = Number(value);
    setField("minPlatformVersion", Number.isFinite(n) ? Math.max(0, Math.round(n)) : 1000);
  });

  bindInput("themeColor", (value) => setField("colors.theme", value));
  bindInput("bgColor", (value) => {
    setField("colors.background", value);
    setField("backgrounds.app.value", value);
  });
  bindInput("textPrimary", (value) => setField("colors.text_primary", value));
  bindInput("textSecondary", (value) => setField("colors.text_secondary", value));
  bindInput("sliderSelected", (value) => setField("colors.slider_selected", value));
  bindInput("sliderUnselected", (value) => setField("colors.slider_unselected", value));

  bindInput("primaryBg", (value) => setField("buttons.primary.bg", value));
  bindInput("primaryText", (value) => setField("buttons.primary.text", value));
  bindInput("dangerBg", (value) => setField("buttons.danger.bg", value));
  bindInput("dangerText", (value) => setField("buttons.danger.text", value));

  byId("themeId").value = state.id;
  byId("themeName").value = state.name;
  byId("themeVersion").value = state.version;
  byId("themeAuthor").value = state.author;
  byId("themeDesc").value = state.description;
  byId("themeMinApp").value = state.minAppVersion;
  byId("themeMinPlatform").value = String(state.minPlatformVersion);

  byId("themeColor").value = rgbaToHex(state.colors.theme, "#00e5ff");
  byId("bgColor").value = rgbaToHex(state.colors.background, "#0d1221");
  byId("textPrimary").value = state.colors.text_primary;
  byId("textSecondary").value = state.colors.text_secondary;
  byId("sliderSelected").value = state.colors.slider_selected;
  byId("sliderUnselected").value = state.colors.slider_unselected;
  byId("primaryBg").value = state.buttons.primary.bg;
  byId("primaryText").value = state.buttons.primary.text;
  byId("dangerBg").value = state.buttons.danger.bg;
  byId("dangerText").value = state.buttons.danger.text;

  byId("resetBtn").addEventListener("click", () => {
    Object.assign(state, clone(DEFAULT_THEME));
    window.location.reload();
  });

  byId("copyBtn").addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(prettyJson(state));
      byId("copyBtn").textContent = "已复制";
      setTimeout(() => {
        byId("copyBtn").innerHTML = `${icon("copy", "icon")} 复制 JSON`;
      }, 1200);
    } catch (_error) {
      byId("copyBtn").textContent = "复制失败";
    }
  });

  byId("downloadJsonBtn").addEventListener("click", () => {
    const blob = new Blob([prettyJson(state)], { type: "application/json;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${state.id || "theme"}.json`;
    a.click();
    URL.revokeObjectURL(url);
  });

  function guessExt(file, fallback = ".png") {
    const name = (file?.name || "").toLowerCase();
    const match = name.match(/\.[a-z0-9]+$/);
    return match ? match[0] : fallback;
  }

  async function readFileAsUint8(file) {
    const buffer = await file.arrayBuffer();
    return new Uint8Array(buffer);
  }

  function bindFileInput(id, key) {
    const input = byId(id);
    input.addEventListener("change", async () => {
      const [file] = input.files || [];
      if (!file) {
        assets[key] = null;
        return;
      }
      assets[key] = file;
    });
  }

  bindFileInput("previewFile", "preview");
  bindFileInput("bgAppFile", "bgApp");
  bindFileInput("primaryBtnFile", "primaryBtn");
  bindFileInput("dangerBtnFile", "dangerBtn");

  byId("downloadZipBtn").addEventListener("click", async () => {
    const themeId = state.id || "my_theme";
    const root = `${themeId}/`;
    const entries = [
      {
        name: `${root}theme.json`,
        data: prettyJson(state),
      },
    ];

    try {
      if (assets.preview) {
        entries.push({
          name: `${root}preview${guessExt(assets.preview, ".png")}`,
          data: await readFileAsUint8(assets.preview),
        });
      }
      if (assets.bgApp) {
        entries.push({
          name: `${root}images/bg_app${guessExt(assets.bgApp, ".png")}`,
          data: await readFileAsUint8(assets.bgApp),
        });
      }
      if (assets.primaryBtn) {
        const ext = guessExt(assets.primaryBtn, ".png");
        entries.push({
          name: `${root}buttons/primary${ext}`,
          data: await readFileAsUint8(assets.primaryBtn),
        });
        state.buttons.primary.image = `buttons/primary${ext}`;
      }
      if (assets.dangerBtn) {
        const ext = guessExt(assets.dangerBtn, ".png");
        entries.push({
          name: `${root}buttons/danger${ext}`,
          data: await readFileAsUint8(assets.dangerBtn),
        });
        state.buttons.danger.image = `buttons/danger${ext}`;
      }

      entries[0].data = prettyJson(state);

      const zipBytes = await buildZip(entries);
      const blob = new Blob([zipBytes], { type: "application/zip" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${themeId}.zip`;
      a.click();
      URL.revokeObjectURL(url);

      byId("downloadZipBtn").textContent = "ZIP 已下载";
      setTimeout(() => {
        byId("downloadZipBtn").textContent = "下载 ZIP 主题包";
      }, 1200);
      applyJsonView();
    } catch (_error) {
      byId("downloadZipBtn").textContent = "ZIP 打包失败";
      setTimeout(() => {
        byId("downloadZipBtn").textContent = "下载 ZIP 主题包";
      }, 1400);
    }
  });

  applyJsonView();
}

function bootstrap() {
  initTheme();

  setIcon(byId("logoIcon"), "logo", "brand-icon");
  setIcon(byId("paletteIcon"), "palette", "icon");
  setIcon(byId("sparkIcon"), "spark", "icon");
  setIcon(byId("checkIcon"), "check", "icon");

  const themeSwitch = byId("themeSwitch");
  renderThemeToggle(themeSwitch);
  themeSwitch.addEventListener("click", () => {
    toggleTheme();
    renderThemeToggle(themeSwitch);
  });

  setupBuilder();
}

bootstrap();
