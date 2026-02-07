#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import AdmZip from "adm-zip";

const IMAGE_EXTENSIONS = new Set([".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"]);
const PREVIEW_CANDIDATES = ["preview.png", "preview.jpg", "preview.jpeg", "preview.webp", "preview.gif"];

function ensureDir(targetPath) {
  fs.mkdirSync(targetPath, { recursive: true });
}

function cleanDirectory(dirPath) {
  ensureDir(dirPath);
  for (const name of fs.readdirSync(dirPath)) {
    const fullPath = path.join(dirPath, name);
    fs.rmSync(fullPath, { recursive: true, force: true });
  }
}

function utcNow() {
  return new Date().toISOString().replace(/\.\d{3}Z$/, "Z");
}

function sanitizeThemeId(rawValue, fallback) {
  const text = String(rawValue || "")
    .trim()
    .toLowerCase()
    .replaceAll("-", "_")
    .replace(/[^a-z0-9_]+/g, "_")
    .replace(/_+/g, "_")
    .replace(/^_+|_+$/g, "");
  return text || fallback;
}

function uniqueThemeId(baseId, used) {
  if (!used.has(baseId)) return baseId;
  let i = 2;
  while (used.has(`${baseId}_${i}`)) i += 1;
  return `${baseId}_${i}`;
}

function normalizePath(raw) {
  return String(raw || "").replaceAll("\\", "/").replace(/^\/+/, "");
}

function safeJoin(base, relativePath) {
  const target = path.resolve(base, relativePath);
  const baseResolved = path.resolve(base);
  if (!target.startsWith(baseResolved)) return null;
  return target;
}

function detectSingleRoot(fileEntries) {
  const roots = new Set();
  for (const entryPath of fileEntries) {
    const normalized = normalizePath(entryPath);
    if (!normalized) continue;
    const first = normalized.split("/")[0];
    if (!first) continue;
    roots.add(first);
    if (roots.size > 1) return null;
  }
  return roots.size === 1 ? Array.from(roots)[0] : null;
}

function decodeBufferToString(buffer) {
  for (const encoding of ["utf8", "utf-8", "latin1"]) {
    try {
      return buffer.toString(encoding);
    } catch (_error) {
      continue;
    }
  }
  return buffer.toString("utf8");
}

function readThemeJsonFromZip(zipPath) {
  const zip = new AdmZip(zipPath);
  const entries = zip.getEntries().filter((entry) => !entry.isDirectory);
  const fileNames = entries.map((entry) => normalizePath(entry.entryName));
  const rootPrefix = detectSingleRoot(fileNames);

  const candidates = [];
  if (rootPrefix) candidates.push(`${rootPrefix}/theme.json`);
  candidates.push("theme.json");
  for (const name of fileNames) {
    if (name.toLowerCase().endsWith("/theme.json")) candidates.push(name);
  }

  let themeEntry = null;
  for (const candidate of candidates) {
    themeEntry = entries.find((entry) => normalizePath(entry.entryName) === candidate);
    if (themeEntry) break;
  }

  if (!themeEntry) {
    throw new Error("Package missing theme.json");
  }

  const text = decodeBufferToString(themeEntry.getData());
  const parsed = JSON.parse(text);
  if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
    throw new Error("theme.json must be object");
  }
  return { themeData: parsed, rootPrefix, zip };
}

function stripRootPrefix(filePath, rootPrefix) {
  const normalized = normalizePath(filePath);
  if (!normalized) return "";
  let next = normalized;
  if (rootPrefix && next.startsWith(`${rootPrefix}/`)) {
    next = next.slice(rootPrefix.length + 1);
  }
  if (!next || next.includes("..") || next.startsWith("/")) return "";
  return next;
}

function extractZip(zip, outputDir, rootPrefix) {
  ensureDir(outputDir);
  for (const entry of zip.getEntries()) {
    if (entry.isDirectory) continue;
    const relativePath = stripRootPrefix(entry.entryName, rootPrefix);
    if (!relativePath) continue;
    const safePath = safeJoin(outputDir, relativePath);
    if (!safePath) continue;
    ensureDir(path.dirname(safePath));
    fs.writeFileSync(safePath, entry.getData());
  }
}

function collectImages(themeDir) {
  const results = [];
  function walk(current, prefix = "") {
    for (const name of fs.readdirSync(current)) {
      const full = path.join(current, name);
      const rel = prefix ? `${prefix}/${name}` : name;
      const stat = fs.statSync(full);
      if (stat.isDirectory()) {
        walk(full, rel);
      } else if (IMAGE_EXTENSIONS.has(path.extname(name).toLowerCase())) {
        results.push(rel.replaceAll("\\", "/"));
      }
    }
  }
  walk(themeDir);
  return results.sort((a, b) => a.localeCompare(b));
}

function pickPreview(images) {
  const map = new Map(images.map((image) => [image.toLowerCase(), image]));
  for (const candidate of PREVIEW_CANDIDATES) {
    if (map.has(candidate)) return map.get(candidate);
  }
  const withPreview = images.find((item) => item.toLowerCase().includes("preview"));
  return withPreview || images[0] || null;
}

function buildGallery(images, preview) {
  const score = (item) => {
    const lower = item.toLowerCase();
    if (preview && item === preview) return 0;
    if (lower.includes("preview")) return 1;
    if (lower.includes("bg") || lower.includes("background")) return 2;
    if (lower.startsWith("images/")) return 3;
    return 4;
  };
  return [...images].sort((a, b) => score(a) - score(b) || a.localeCompare(b)).slice(0, 8);
}

function relWebPath(fromRoot, target) {
  return `./${path.relative(fromRoot, target).replaceAll("\\", "/")}`;
}

function buildCatalog(repoRoot) {
  const packagesRoot = path.join(repoRoot, "packages");
  const themesRoot = path.join(repoRoot, "themes");
  const downloadsRoot = path.join(repoRoot, "downloads");
  const dataRoot = path.join(repoRoot, "data");

  cleanDirectory(themesRoot);
  cleanDirectory(downloadsRoot);
  ensureDir(dataRoot);

  const zipFiles = fs
    .readdirSync(packagesRoot)
    .filter((name) => name.toLowerCase().endsWith(".zip"))
    .map((name) => path.join(packagesRoot, name))
    .sort((a, b) => path.basename(a).localeCompare(path.basename(b), "zh-CN"));

  const themes = [];
  const warnings = [];
  const usedIds = new Set();

  for (const zipPath of zipFiles) {
    try {
      const { themeData, rootPrefix, zip } = readThemeJsonFromZip(zipPath);
      const fallbackId = sanitizeThemeId(path.basename(zipPath, ".zip"), "theme");
      const themeId = uniqueThemeId(sanitizeThemeId(themeData.id, fallbackId), usedIds);
      usedIds.add(themeId);

      const themeDir = path.join(themesRoot, themeId);
      extractZip(zip, themeDir, rootPrefix);

      const downloadTarget = path.join(downloadsRoot, path.basename(zipPath));
      fs.copyFileSync(zipPath, downloadTarget);

      const images = collectImages(themeDir);
      const preview = pickPreview(images);
      const gallery = buildGallery(images, preview);
      const zipStat = fs.statSync(zipPath);

      themes.push({
        id: themeId,
        sourceId: themeData.id || themeId,
        name: themeData.name || themeId,
        version: themeData.version || "1.0.0",
        author: themeData.author || "未知作者",
        description: themeData.description || "暂无描述",
        schemaVersion: themeData.schemaVersion || "1.0",
        minAppVersion: themeData.minAppVersion || "1.0.0",
        minPlatformVersion: Number.isFinite(Number(themeData.minPlatformVersion))
          ? Number(themeData.minPlatformVersion)
          : 1000,
        tags: Array.isArray(themeData.tags) ? themeData.tags : [],
        updatedAt: new Date(zipStat.mtimeMs).toISOString().replace(/\.\d{3}Z$/, "Z"),
        package: {
          fileName: path.basename(zipPath),
          sizeBytes: zipStat.size,
          downloadUrl: relWebPath(repoRoot, downloadTarget),
        },
        paths: {
          themeDir: relWebPath(repoRoot, themeDir),
          themeJson: relWebPath(repoRoot, path.join(themeDir, "theme.json")),
          preview: preview ? relWebPath(repoRoot, path.join(themeDir, preview)) : null,
          gallery: gallery.map((item) => relWebPath(repoRoot, path.join(themeDir, item))),
        },
      });
    } catch (error) {
      warnings.push(`${path.basename(zipPath)}: ${error.message}`);
    }
  }

  themes.sort((a, b) => String(a.name || "").localeCompare(String(b.name || ""), "zh-CN"));
  const catalog = {
    schemaVersion: "1.0",
    generatedAt: utcNow(),
    count: themes.length,
    themes,
    warnings,
  };

  fs.writeFileSync(path.join(dataRoot, "themes.json"), `${JSON.stringify(catalog, null, 2)}\n`, "utf8");
  return catalog;
}

const repoRoot = process.cwd();
const catalog = buildCatalog(repoRoot);
console.log(`Built catalog with ${catalog.count} theme(s)`);
if (catalog.warnings.length) {
  console.log("警告：");
  for (const item of catalog.warnings) {
    console.log(`- ${item}`);
  }
}
