#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

const repoRoot = process.cwd();

const REQUIRED_FILES = [
  "index.html",
  "theme.html",
  "builder.html",
  "guide.html",
  "404.html",
  "assets/css/app.css",
  "assets/js/main.js",
  "assets/js/theme-detail.js",
  "assets/js/builder.js",
  "assets/js/catalog.js",
  "data/themes.json",
];

function read(filePath) {
  return fs.readFileSync(path.join(repoRoot, filePath), "utf8");
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

function verifyFilesExist() {
  for (const relative of REQUIRED_FILES) {
    const full = path.join(repoRoot, relative);
    assert(fs.existsSync(full), `Missing required file: ${relative}`);
  }
}

function verifyRelativeLinks() {
  const htmlFiles = ["index.html", "theme.html", "builder.html", "guide.html", "404.html"];
  for (const file of htmlFiles) {
    const content = read(file);
    assert(!content.includes('href="/'), `${file} has absolute href path`);
    assert(!content.includes('src="/'), `${file} has absolute src path`);
  }

  const catalogJs = read("assets/js/catalog.js");
  assert(catalogJs.includes('const CATALOG_URL = "./data/themes.json";'), "catalog.js must use relative catalog URL");
}

function verifyCatalog() {
  const data = JSON.parse(read("data/themes.json"));
  assert(Array.isArray(data.themes), "themes.json missing themes array");
  for (const theme of data.themes) {
    assert(String(theme.package?.downloadUrl || "").startsWith("./downloads/"), "downloadUrl must be relative");
    assert(String(theme.paths?.themeJson || "").startsWith("./themes/"), "themeJson path must be relative");
    if (theme.paths?.preview) {
      assert(String(theme.paths.preview).startsWith("./themes/"), "preview path must be relative");
    }
  }
}

function verifyChineseUI() {
  const checks = [
    ["index.html", "主题商店"],
    ["builder.html", "主题制作工具"],
    ["theme.html", "主题详情"],
    ["guide.html", "部署指南"],
  ];

  for (const [file, text] of checks) {
    const content = read(file);
    assert(content.includes(text), `${file} should contain Chinese UI text: ${text}`);
  }

  const catalogJs = read("assets/js/catalog.js");
  assert(!catalogJs.includes("Failed to load catalog"), "catalog.js should not include English error message");
}

function main() {
  verifyFilesExist();
  verifyRelativeLinks();
  verifyCatalog();
  verifyChineseUI();
  console.log("站点校验通过");
}

main();
