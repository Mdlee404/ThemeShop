#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import AdmZip from "adm-zip";

const SCHEMA_VERSION = "1.0";
const ID_RE = /^[a-z0-9_]+$/;
const REQUIRED_COLOR_KEYS = [
  "theme",
  "background",
  "text_primary",
  "text_secondary",
  "slider_selected",
  "slider_block",
  "slider_unselected",
];

const DEFAULT_THEME = {
  schemaVersion: SCHEMA_VERSION,
  id: "my_theme",
  name: "新主题",
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
  lyric: {
    active: "#00E5FF",
    normal: "#FFF2D9",
    active_bg: "rgba(0,229,255,0.25)",
  },
  icons: { dark_mode: false, path: "icons" },
  assets: { base: ".", images: "images", buttons: "buttons" },
};

function clone(data) {
  return JSON.parse(JSON.stringify(data));
}

function readJson(jsonPath) {
  return JSON.parse(fs.readFileSync(jsonPath, "utf8"));
}

function writeJson(jsonPath, data) {
  fs.mkdirSync(path.dirname(jsonPath), { recursive: true });
  fs.writeFileSync(jsonPath, `${JSON.stringify(data, null, 2)}\n`, "utf8");
}

function validateThemeData(data) {
  const errors = [];
  if (String(data?.schemaVersion || "") !== SCHEMA_VERSION) {
    errors.push(`schemaVersion must be ${SCHEMA_VERSION}`);
  }
  const themeId = String(data?.id || "");
  if (!ID_RE.test(themeId)) {
    errors.push("id must match ^[a-z0-9_]+$");
  }
  if (!String(data?.name || "").trim()) {
    errors.push("name is required");
  }
  const colors = data?.colors;
  if (!colors || typeof colors !== "object" || Array.isArray(colors)) {
    errors.push("colors must be object");
  } else {
    for (const key of REQUIRED_COLOR_KEYS) {
      if (!String(colors[key] || "").trim()) {
        errors.push(`colors.${key} is required`);
      }
    }
  }
  return errors;
}

function parseArgs(argv) {
  const command = argv[2] || "";
  const args = {};
  for (let i = 3; i < argv.length; i += 1) {
    const token = argv[i];
    if (!token.startsWith("--")) continue;
    const key = token.slice(2);
    const value = argv[i + 1] && !argv[i + 1].startsWith("--") ? argv[++i] : "true";
    args[key] = value;
  }
  return { command, args };
}

function cmdInit(args) {
  const id = String(args.id || "").trim().toLowerCase();
  if (!ID_RE.test(id)) {
    throw new Error("--id must match ^[a-z0-9_]+$");
  }
  const themeDir = path.resolve(args.dir || id);
  const themeJson = path.join(themeDir, "theme.json");
  if (fs.existsSync(themeJson) && args.force !== "true") {
    throw new Error(`${themeJson} already exists, use --force true`);
  }

  const data = clone(DEFAULT_THEME);
  data.id = id;
  data.name = args.name || "新主题";
  data.author = args.author || "";
  data.description = args.description || "";

  writeJson(themeJson, data);
  fs.mkdirSync(path.join(themeDir, "icons"), { recursive: true });
  fs.mkdirSync(path.join(themeDir, "images"), { recursive: true });
  fs.mkdirSync(path.join(themeDir, "buttons"), { recursive: true });
  const preview = path.join(themeDir, "preview.png");
  if (!fs.existsSync(preview)) fs.writeFileSync(preview, Buffer.alloc(0));

  console.log(`created theme template: ${themeDir}`);
}

function cmdValidate(args) {
  const filePath = path.resolve(args.file || "");
  if (!filePath || !fs.existsSync(filePath)) {
    throw new Error("--file not found");
  }
  const data = readJson(filePath);
  const errors = validateThemeData(data);
  if (errors.length) {
    console.error("validation failed:");
    for (const error of errors) console.error(`- ${error}`);
    process.exitCode = 1;
    return;
  }
  console.log("validation passed");
}

function cmdPack(args) {
  const dir = path.resolve(args.dir || "");
  const out = path.resolve(args.out || "");
  if (!dir || !fs.existsSync(dir) || !fs.statSync(dir).isDirectory()) {
    throw new Error("--dir is invalid");
  }
  if (!out) throw new Error("--out is required");

  const themeJson = path.join(dir, "theme.json");
  if (!fs.existsSync(themeJson)) {
    throw new Error("theme.json is required in --dir");
  }
  const data = readJson(themeJson);
  const errors = validateThemeData(data);
  if (errors.length) {
    throw new Error(`validation failed: ${errors.join("; ")}`);
  }

  fs.mkdirSync(path.dirname(out), { recursive: true });
  const zip = new AdmZip();
  const root = path.basename(dir);

  function walk(current, rel = "") {
    for (const name of fs.readdirSync(current)) {
      const full = path.join(current, name);
      const nextRel = rel ? `${rel}/${name}` : name;
      const stat = fs.statSync(full);
      if (stat.isDirectory()) walk(full, nextRel);
      else zip.addFile(`${root}/${nextRel}`.replaceAll("\\", "/"), fs.readFileSync(full));
    }
  }

  walk(dir);
  zip.writeZip(out);
  console.log(`packed: ${out}`);
}

function printHelp() {
  console.log(`Usage:
  node tools/theme-builder-reference.mjs init --id aurora [--name 极光] [--author foo]
  node tools/theme-builder-reference.mjs validate --file ./aurora/theme.json
  node tools/theme-builder-reference.mjs pack --dir ./aurora --out ./packages/aurora.zip`);
}

function main() {
  const { command, args } = parseArgs(process.argv);
  if (!command || command === "help" || command === "--help") {
    printHelp();
    return;
  }

  if (command === "init") return cmdInit(args);
  if (command === "validate") return cmdValidate(args);
  if (command === "pack") return cmdPack(args);

  throw new Error(`Unknown command: ${command}`);
}

try {
  main();
} catch (error) {
  console.error(`error: ${error.message}`);
  process.exit(1);
}

