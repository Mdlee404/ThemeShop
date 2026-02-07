import json
import os
import re
import shutil
import zipfile
import tkinter as tk
import tkinter.font as tkfont
from tkinter import colorchooser, ttk, filedialog, messagebox, simpledialog


THEME_SCHEMA_VERSION = "1.0"
ID_PATTERN = re.compile(r"^[a-z0-9_]+$")
RGBA_RE = re.compile(r"rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)(?:,\\s*([0-9.]+))?\\)")

UI_PALETTE = {
    "bg": "#f6f7fb",
    "card": "#ffffff",
    "border": "#e5e7ee",
    "text": "#1f2937",
    "muted": "#6b7280",
    "accent": "#2563eb",
    "accent_soft": "#dbeafe",
    "danger": "#ef4444",
}

REQUIRED_COLOR_KEYS = [
    "theme",
    "background",
    "text_primary",
    "text_secondary",
    "slider_selected",
    "slider_block",
    "slider_unselected",
]

DEFAULT_COLORS = {
    "theme": "#00E5FF",
    "background": "#f0f0f0",
    "text_primary": "rgba(0,0,0,0.87)",
    "text_secondary": "rgba(0,0,0,0.6)",
    "slider_selected": "#00E5FF",
    "slider_block": "#00E5FF",
    "slider_unselected": "rgba(0,0,0,0.1)",
}

DEFAULT_TEXT = {
    "title": "rgba(0,0,0,0.87)",
    "body": "rgba(0,0,0,0.8)",
    "caption": "rgba(0,0,0,0.6)",
    "danger": "#FF3B30",
}

DEFAULT_LYRIC = {
    "active": "#00E5FF",
    "normal": "#000000",
    "active_bg": "rgba(0,229,255,0.2)",
}

REQUIRED_ICON_NAMES = [
    "\u9996\u9875.png",
    "\u97f3\u91cf.png",
    "\u97f3\u4e50.png",
    "\u95f9\u949f.png",
    "\u8fd4\u56de.png",
    "\u8ba2\u9605.png",
    "\u8b66\u544a.png",
    "\u83dc\u5355.png",
    "\u6682\u505c.png",
    "\u64ad\u653e.png",
    "\u641c\u7d22.png",
    "\u559c\u6b22.png",
    "\u52a0\u8f7d.png",
    "\u52a0.png",
    "\u5220\u9664.png",
    "\u51cf.png",
    "\u5173\u4e8e.png",
    "\u5149\u76d8.png",
    "\u4e0d\u559c\u6b22.png",
    "\u4e0b\u8f7d.png",
    "\u4e0b\u4e00\u66f2.png",
    "\u4e0a\u4e00\u66f2.png",
    "logo.png",
]


def default_theme(theme_id="new_theme"):
    return {
        "schemaVersion": THEME_SCHEMA_VERSION,
        "id": theme_id,
        "name": "新主题",
        "version": "1.0.0",
        "author": "",
        "description": "",
        "minAppVersion": "1.0.0",
        "minPlatformVersion": 1000,
        "colors": dict(DEFAULT_COLORS),
        "text": dict(DEFAULT_TEXT),
        "backgrounds": {
            "app": {"type": "color", "value": "#f0f0f0"},
            "card": {"type": "color", "value": "rgba(255,255,255,0.1)"},
        },
        "buttons": {
            "primary": {"bg": "rgba(0,229,255,0.2)", "text": "#00E5FF"},
            "danger": {"bg": "rgba(255,59,48,0.2)", "text": "#FF3B30"},
        },
        "lyric": dict(DEFAULT_LYRIC),
        "icons": {"dark_mode": False, "path": "icons"},
        "assets": {"base": ".", "images": "images", "buttons": "buttons"},
    }


def normalize_theme(data):
    if not isinstance(data, dict):
        data = {}
    data.setdefault("schemaVersion", THEME_SCHEMA_VERSION)
    data.setdefault("id", "new_theme")
    data.setdefault("name", "新主题")
    data.setdefault("version", "1.0.0")
    data.setdefault("author", "")
    data.setdefault("description", "")
    data.setdefault("minAppVersion", "1.0.0")
    data.setdefault("minPlatformVersion", 1000)

    colors = data.get("colors") or {}
    for key in REQUIRED_COLOR_KEYS:
        colors.setdefault(key, DEFAULT_COLORS.get(key, "#000000"))
    data["colors"] = colors

    data["text"] = data.get("text") or dict(DEFAULT_TEXT)
    data["backgrounds"] = data.get("backgrounds") or {}
    data["buttons"] = data.get("buttons") or {}
    data["lyric"] = data.get("lyric") or dict(DEFAULT_LYRIC)
    data["icons"] = data.get("icons") or {"dark_mode": False, "path": "icons"}
    data["assets"] = data.get("assets") or {"base": ".", "images": "images", "buttons": "buttons"}
    return data


def read_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def rel_path(path):
    return path.replace("\\", "/")


def parse_color(value, fallback="#000000"):
    if value is None:
        return fallback
    text = str(value).strip()
    if not text:
        return fallback
    if text.startswith("#"):
        return text
    match = RGBA_RE.match(text)
    if match:
        r = max(0, min(255, int(match.group(1))))
        g = max(0, min(255, int(match.group(2))))
        b = max(0, min(255, int(match.group(3))))
        return f"#{r:02x}{g:02x}{b:02x}"
    return fallback


def parse_rgba(value):
    if value is None:
        return None
    text = str(value).strip().lower()
    if text.startswith("#") and len(text) in (4, 7):
        if len(text) == 4:
            r = int(text[1] * 2, 16)
            g = int(text[2] * 2, 16)
            b = int(text[3] * 2, 16)
        else:
            r = int(text[1:3], 16)
            g = int(text[3:5], 16)
            b = int(text[5:7], 16)
        return r, g, b, None
    match = RGBA_RE.match(text)
    if match:
        r = int(match.group(1))
        g = int(match.group(2))
        b = int(match.group(3))
        a = match.group(4)
        return r, g, b, float(a) if a is not None else None
    return None


def apply_modern_theme(root):
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    default_font = tkfont.nametofont("TkDefaultFont")
    default_font.configure(size=10, family="Microsoft YaHei UI")
    small_font = tkfont.Font(family=default_font.actual("family"), size=9)
    heading_font = tkfont.Font(family=default_font.actual("family"), size=10, weight="bold")
    title_font = tkfont.Font(family=default_font.actual("family"), size=12, weight="bold")

    root.configure(bg=UI_PALETTE["bg"])

    style.configure("TFrame", background=UI_PALETTE["bg"])
    style.configure("Card.TFrame", background=UI_PALETTE["card"])
    style.configure("Header.TFrame", background=UI_PALETTE["bg"])
    style.configure("TLabel", background=UI_PALETTE["card"], foreground=UI_PALETTE["text"], font=default_font)
    style.configure("Muted.TLabel", background=UI_PALETTE["bg"], foreground=UI_PALETTE["muted"], font=small_font)
    style.configure("Title.TLabel", background=UI_PALETTE["bg"], foreground=UI_PALETTE["text"], font=title_font)
    style.configure("HeaderValue.TLabel", background=UI_PALETTE["bg"], foreground=UI_PALETTE["text"], font=default_font)

    style.configure(
        "TButton",
        font=default_font,
        padding=(10, 6),
        background=UI_PALETTE["card"],
        foreground=UI_PALETTE["text"],
    )
    style.map(
        "TButton",
        background=[("active", UI_PALETTE["accent_soft"])],
        foreground=[("disabled", UI_PALETTE["muted"])],
    )
    style.configure(
        "Accent.TButton",
        background=UI_PALETTE["accent"],
        foreground="#ffffff",
    )
    style.map(
        "Accent.TButton",
        background=[("active", "#1d4ed8")],
    )

    style.configure(
        "Treeview",
        font=default_font,
        rowheight=26,
        background=UI_PALETTE["card"],
        fieldbackground=UI_PALETTE["card"],
        foreground=UI_PALETTE["text"],
        bordercolor=UI_PALETTE["border"],
        lightcolor=UI_PALETTE["border"],
        darkcolor=UI_PALETTE["border"],
    )
    style.configure(
        "Treeview.Heading",
        font=heading_font,
        background=UI_PALETTE["bg"],
        foreground=UI_PALETTE["text"],
        relief="flat",
    )

    style.configure("TNotebook", background=UI_PALETTE["bg"], borderwidth=0)
    style.configure(
        "TNotebook.Tab",
        background=UI_PALETTE["bg"],
        foreground=UI_PALETTE["muted"],
        padding=(12, 6),
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", UI_PALETTE["card"])],
        foreground=[("selected", UI_PALETTE["text"])],
    )

    style.configure("TEntry", padding=6)
    style.configure("TCheckbutton", background=UI_PALETTE["card"], foreground=UI_PALETTE["text"])

def build_theme_output(data):
    order = [
        "schemaVersion",
        "id",
        "name",
        "version",
        "author",
        "description",
        "minAppVersion",
        "minPlatformVersion",
        "colors",
        "text",
        "backgrounds",
        "buttons",
        "lyric",
        "icons",
        "assets",
    ]
    output = {}
    for key in order:
        if key in data:
            output[key] = data[key]
    for key in data:
        if key not in output:
            output[key] = data[key]
    return output


def validate_id(value):
    return bool(ID_PATTERN.match(value))


def validate_paths(data):
    warnings = []
    assets = data.get("assets") or {}
    for key in ("base", "images", "buttons"):
        val = assets.get(key, "")
        if ".." in str(val):
            warnings.append(f"assets.{key} 包含 \"..\": {val}")
    return warnings


def copy_into_project(project_dir, src_path, subdir):
    dest_dir = os.path.join(project_dir, subdir)
    ensure_dir(dest_dir)
    filename = os.path.basename(src_path)
    dest_path = os.path.join(dest_dir, filename)
    shutil.copy2(src_path, dest_path)
    rel = os.path.relpath(dest_path, project_dir)
    return rel_path(rel)


def list_missing_icons(icons_dir):
    missing = []
    for name in REQUIRED_ICON_NAMES:
        if not os.path.exists(os.path.join(icons_dir, name)):
            missing.append(name)
    return missing


class KeyValueDialog(tk.Toplevel):
    def __init__(self, parent, title, key="", value="", readonly_key=False):
        super().__init__(parent)
        self.result = None
        self.title(title)
        self.resizable(False, False)
        self.key_var = tk.StringVar(value=key)
        self.value_var = tk.StringVar(value=value)
        self.original_value = value

        ttk.Label(self, text="键").grid(row=0, column=0, padx=8, pady=8, sticky="w")
        key_entry = ttk.Entry(self, textvariable=self.key_var, width=32)
        key_entry.grid(row=0, column=1, padx=8, pady=8, sticky="ew")
        if readonly_key:
            key_entry.configure(state="readonly")

        ttk.Label(self, text="值").grid(row=1, column=0, padx=8, pady=8, sticky="w")
        value_entry = ttk.Entry(self, textvariable=self.value_var, width=32)
        value_entry.grid(row=1, column=1, padx=8, pady=8, sticky="ew")
        ttk.Button(self, text="选颜色", command=self.choose_color).grid(
            row=1, column=2, padx=6, pady=8, sticky="ew"
        )

        btns = ttk.Frame(self)
        btns.grid(row=2, column=0, columnspan=3, padx=8, pady=8, sticky="e")
        ttk.Button(btns, text="取消", command=self.destroy).pack(side="right", padx=4)
        ttk.Button(btns, text="确定", command=self.on_ok).pack(side="right", padx=4)

        self.bind("<Return>", lambda _e: self.on_ok())
        self.bind("<Escape>", lambda _e: self.destroy())
        key_entry.focus_set()

    def on_ok(self):
        key = self.key_var.get().strip()
        if not key:
            messagebox.showerror("键无效", "键不能为空。")
            return
        self.result = (key, self.value_var.get().strip())
        self.destroy()

    def choose_color(self):
        current = self.value_var.get().strip()
        initial = parse_color(current or self.original_value or "#000000", "#000000")
        chosen = colorchooser.askcolor(color=initial, title="选择颜色")
        if not chosen or not chosen[1]:
            return
        hex_color = chosen[1]
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        text = (current or "").lower()
        if text.startswith("rgba"):
            match = RGBA_RE.match(text)
            alpha = match.group(4) if match and match.group(4) is not None else "1"
            self.value_var.set(f"rgba({r},{g},{b},{alpha})")
        elif text.startswith("rgb"):
            self.value_var.set(f"rgb({r},{g},{b})")
        else:
            self.value_var.set(hex_color)


class BackgroundDialog(tk.Toplevel):
    def __init__(self, parent, title, data, project_dir):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.result = None
        self.project_dir = project_dir

        self.key_var = tk.StringVar(value=data.get("key", ""))
        self.type_var = tk.StringVar(value=data.get("type", "color"))
        self.value_var = tk.StringVar(value=data.get("value", ""))
        self.fit_var = tk.StringVar(value=data.get("objectFit", ""))

        ttk.Label(self, text="键").grid(row=0, column=0, padx=8, pady=6, sticky="w")
        ttk.Entry(self, textvariable=self.key_var, width=30).grid(
            row=0, column=1, padx=8, pady=6, sticky="ew"
        )

        ttk.Label(self, text="类型").grid(row=1, column=0, padx=8, pady=6, sticky="w")
        type_combo = ttk.Combobox(self, textvariable=self.type_var, values=["color", "image"], width=27)
        type_combo.grid(row=1, column=1, padx=8, pady=6, sticky="ew")
        type_combo.state(["readonly"])

        ttk.Label(self, text="值").grid(row=2, column=0, padx=8, pady=6, sticky="w")
        ttk.Entry(self, textvariable=self.value_var, width=30).grid(
            row=2, column=1, padx=8, pady=6, sticky="ew"
        )

        ttk.Label(self, text="适配").grid(row=3, column=0, padx=8, pady=6, sticky="w")
        ttk.Entry(self, textvariable=self.fit_var, width=30).grid(
            row=3, column=1, padx=8, pady=6, sticky="ew"
        )

        actions = ttk.Frame(self)
        actions.grid(row=4, column=0, columnspan=2, padx=8, pady=6, sticky="w")
        ttk.Button(actions, text="选择图片", command=self.browse_image).pack(side="left")

        btns = ttk.Frame(self)
        btns.grid(row=5, column=0, columnspan=2, padx=8, pady=8, sticky="e")
        ttk.Button(btns, text="取消", command=self.destroy).pack(side="right", padx=4)
        ttk.Button(btns, text="确定", command=self.on_ok).pack(side="right", padx=4)

        self.bind("<Return>", lambda _e: self.on_ok())
        self.bind("<Escape>", lambda _e: self.destroy())

    def browse_image(self):
        if not self.project_dir:
            messagebox.showerror("未打开主题", "请先新建或打开主题。")
            return
        src = filedialog.askopenfilename(
            title="选择背景图片",
            filetypes=[("图片文件", "*.png;*.jpg;*.jpeg;*.webp"), ("所有文件", "*.*")],
        )
        if not src:
            return
        rel = copy_into_project(self.project_dir, src, "images")
        self.value_var.set(rel)
        self.type_var.set("image")

    def on_ok(self):
        key = self.key_var.get().strip()
        if not key:
            messagebox.showerror("键无效", "键不能为空。")
            return
        value = self.value_var.get().strip()
        if not value:
            messagebox.showerror("值无效", "值不能为空。")
            return
        self.result = {
            "key": key,
            "type": self.type_var.get().strip(),
            "value": value,
            "objectFit": self.fit_var.get().strip(),
        }
        self.destroy()


class ButtonDialog(tk.Toplevel):
    def __init__(self, parent, title, data, project_dir):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.result = None
        self.project_dir = project_dir

        self.key_var = tk.StringVar(value=data.get("key", ""))
        self.bg_var = tk.StringVar(value=data.get("bg", ""))
        self.text_var = tk.StringVar(value=data.get("text", ""))
        self.border_var = tk.StringVar(value=data.get("border", ""))
        self.image_var = tk.StringVar(value=data.get("image", ""))

        ttk.Label(self, text="键").grid(row=0, column=0, padx=8, pady=6, sticky="w")
        ttk.Entry(self, textvariable=self.key_var, width=30).grid(
            row=0, column=1, padx=8, pady=6, sticky="ew"
        )

        ttk.Label(self, text="背景").grid(row=1, column=0, padx=8, pady=6, sticky="w")
        ttk.Entry(self, textvariable=self.bg_var, width=30).grid(
            row=1, column=1, padx=8, pady=6, sticky="ew"
        )

        ttk.Label(self, text="文字").grid(row=2, column=0, padx=8, pady=6, sticky="w")
        ttk.Entry(self, textvariable=self.text_var, width=30).grid(
            row=2, column=1, padx=8, pady=6, sticky="ew"
        )

        ttk.Label(self, text="边框").grid(row=3, column=0, padx=8, pady=6, sticky="w")
        ttk.Entry(self, textvariable=self.border_var, width=30).grid(
            row=3, column=1, padx=8, pady=6, sticky="ew"
        )

        ttk.Label(self, text="图片").grid(row=4, column=0, padx=8, pady=6, sticky="w")
        ttk.Entry(self, textvariable=self.image_var, width=30).grid(
            row=4, column=1, padx=8, pady=6, sticky="ew"
        )

        actions = ttk.Frame(self)
        actions.grid(row=5, column=0, columnspan=2, padx=8, pady=6, sticky="w")
        ttk.Button(actions, text="选择图片", command=self.browse_image).pack(side="left")

        btns = ttk.Frame(self)
        btns.grid(row=6, column=0, columnspan=2, padx=8, pady=8, sticky="e")
        ttk.Button(btns, text="取消", command=self.destroy).pack(side="right", padx=4)
        ttk.Button(btns, text="确定", command=self.on_ok).pack(side="right", padx=4)

        self.bind("<Return>", lambda _e: self.on_ok())
        self.bind("<Escape>", lambda _e: self.destroy())

    def browse_image(self):
        if not self.project_dir:
            messagebox.showerror("未打开主题", "请先新建或打开主题。")
            return
        src = filedialog.askopenfilename(
            title="选择按钮图片",
            filetypes=[("图片文件", "*.png;*.jpg;*.jpeg;*.webp"), ("所有文件", "*.*")],
        )
        if not src:
            return
        rel = copy_into_project(self.project_dir, src, "buttons")
        self.image_var.set(rel)

    def on_ok(self):
        key = self.key_var.get().strip()
        if not key:
            messagebox.showerror("键无效", "键不能为空。")
            return
        self.result = {
            "key": key,
            "bg": self.bg_var.get().strip(),
            "text": self.text_var.get().strip(),
            "border": self.border_var.get().strip(),
            "image": self.image_var.get().strip(),
        }
        self.destroy()


class ThemeToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title("主题制作工具")
        self.project_dir = None
        self.theme_data = default_theme()
        self.preview_image = None
        self.preview_tags = []
        self.preview_hover_key = None
        self.preview_status_var = tk.StringVar(value="")
        self.tab_frames = {}
        self.lyric_entries = {}

        self.project_var = tk.StringVar(value="未加载项目")
        self.build_ui()
        self.load_theme_into_ui()

    def build_ui(self):
        self.root.minsize(1100, 720)

        header = ttk.Frame(self.root, style="Header.TFrame")
        header.pack(fill="x", padx=16, pady=10)

        title_block = ttk.Frame(header, style="Header.TFrame")
        title_block.pack(side="left")
        ttk.Label(title_block, text="主题制作工具", style="Title.TLabel").pack(anchor="w")
        ttk.Label(title_block, text="遵循 theme.md 规范生成主题包", style="Muted.TLabel").pack(anchor="w")

        project_block = ttk.Frame(header, style="Header.TFrame")
        project_block.pack(side="left", padx=20)
        ttk.Label(project_block, text="当前项目", style="Muted.TLabel").pack(anchor="w")
        ttk.Label(project_block, textvariable=self.project_var, style="HeaderValue.TLabel").pack(anchor="w")

        actions = ttk.Frame(header, style="Header.TFrame")
        actions.pack(side="right")
        ttk.Button(actions, text="新建", command=self.new_project).pack(side="right", padx=4)
        ttk.Button(actions, text="打开", command=self.open_project).pack(side="right", padx=4)
        ttk.Button(actions, text="保存", command=self.save_project, style="Accent.TButton").pack(
            side="right", padx=4
        )
        ttk.Button(actions, text="导出压缩包", command=self.export_zip, style="Accent.TButton").pack(
            side="right", padx=4
        )

        content = ttk.PanedWindow(self.root, orient="horizontal")
        content.pack(fill="both", expand=True, padx=16, pady=10)

        left = ttk.Frame(content, style="TFrame")
        right = ttk.Frame(content, style="TFrame")
        content.add(left, weight=3)
        content.add(right, weight=2)

        notebook_container = ttk.Frame(left, style="Card.TFrame")
        notebook_container.pack(fill="both", expand=True)
        self.notebook = ttk.Notebook(notebook_container)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=8)

        self.build_general_tab()
        self.build_colors_tab()
        self.build_text_tab()
        self.build_backgrounds_tab()
        self.build_buttons_tab()
        self.build_lyric_tab()
        self.build_icons_tab()
        self.build_assets_tab()
        # 省略图片映射页，改为直接在对应位置选图
        self.build_preview_panel(right)
        self.notebook.bind("<<NotebookTabChanged>>", lambda _e: self.refresh_preview())

    def build_general_tab(self):
        frame = ttk.Frame(self.notebook, style="Card.TFrame", padding=12)
        self.notebook.add(frame, text="基础信息")
        self.tab_frames["基础信息"] = frame

        self.id_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.desc_var = tk.StringVar()
        self.version_var = tk.StringVar()
        self.author_var = tk.StringVar()
        self.min_app_var = tk.StringVar()
        self.min_platform_var = tk.StringVar()

        fields = [
            ("ID", self.id_var),
            ("名称", self.name_var),
            ("描述", self.desc_var),
            ("版本", self.version_var),
            ("作者", self.author_var),
            ("最低应用版本", self.min_app_var),
            ("最低平台版本", self.min_platform_var),
        ]
        for idx, (label, var) in enumerate(fields):
            ttk.Label(frame, text=label).grid(row=idx, column=0, padx=8, pady=6, sticky="w")
            ttk.Entry(frame, textvariable=var, width=40).grid(
                row=idx, column=1, padx=8, pady=6, sticky="ew"
            )

        frame.columnconfigure(1, weight=1)

    def build_colors_tab(self):
        frame = ttk.Frame(self.notebook, style="Card.TFrame", padding=8)
        self.notebook.add(frame, text="颜色")
        self.tab_frames["颜色"] = frame
        self.colors_tree = self.make_tree(frame, ["键", "值"])
        self.colors_tree.pack(fill="both", expand=True, padx=6, pady=6)
        self.add_tree_buttons(frame, self.colors_tree, self.add_color, self.edit_color, self.remove_color)

    def build_text_tab(self):
        frame = ttk.Frame(self.notebook, style="Card.TFrame", padding=8)
        self.notebook.add(frame, text="文字")
        self.tab_frames["文字"] = frame
        self.text_tree = self.make_tree(frame, ["键", "值"])
        self.text_tree.pack(fill="both", expand=True, padx=6, pady=6)
        self.add_tree_buttons(frame, self.text_tree, self.add_text, self.edit_text, self.remove_text)

    def build_backgrounds_tab(self):
        frame = ttk.Frame(self.notebook, style="Card.TFrame", padding=8)
        self.notebook.add(frame, text="背景")
        self.tab_frames["背景"] = frame
        quick = ttk.LabelFrame(frame, text="应用背景（快捷设置）")
        quick.pack(fill="x", padx=6, pady=6)

        self.app_bg_type_var = tk.StringVar(value="color")
        self.app_bg_value_var = tk.StringVar(value="")

        ttk.Label(quick, text="类型").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        type_combo = ttk.Combobox(quick, textvariable=self.app_bg_type_var, values=["color", "image"], width=12)
        type_combo.grid(row=0, column=1, padx=6, pady=6, sticky="w")
        type_combo.state(["readonly"])

        ttk.Label(quick, text="值").grid(row=0, column=2, padx=6, pady=6, sticky="w")
        ttk.Entry(quick, textvariable=self.app_bg_value_var, width=36).grid(
            row=0, column=3, padx=6, pady=6, sticky="ew"
        )
        ttk.Button(quick, text="选择图片", command=self.browse_app_background).grid(
            row=0, column=4, padx=6, pady=6
        )
        ttk.Button(quick, text="应用到背景", command=self.apply_app_background).grid(
            row=0, column=5, padx=6, pady=6
        )
        quick.columnconfigure(3, weight=1)

        self.backgrounds_tree = self.make_tree(frame, ["键", "类型", "值", "适配"])
        self.backgrounds_tree.pack(fill="both", expand=True, padx=6, pady=6)
        self.add_tree_buttons(
            frame, self.backgrounds_tree, self.add_background, self.edit_background, self.remove_background
        )

    def build_buttons_tab(self):
        frame = ttk.Frame(self.notebook, style="Card.TFrame", padding=8)
        self.notebook.add(frame, text="按钮")
        self.tab_frames["按钮"] = frame
        self.buttons_tree = self.make_tree(frame, ["键", "背景", "文字", "边框", "图片"])
        self.buttons_tree.pack(fill="both", expand=True, padx=6, pady=6)
        self.add_tree_buttons(frame, self.buttons_tree, self.add_button, self.edit_button, self.remove_button)

    def build_lyric_tab(self):
        frame = ttk.Frame(self.notebook, style="Card.TFrame", padding=12)
        self.notebook.add(frame, text="歌词")
        self.tab_frames["歌词"] = frame
        self.lyric_vars = {
            "active": tk.StringVar(),
            "normal": tk.StringVar(),
            "active_bg": tk.StringVar(),
        }
        for idx, key in enumerate(["active", "normal", "active_bg"]):
            ttk.Label(frame, text=key).grid(row=idx, column=0, padx=8, pady=6, sticky="w")
            entry = ttk.Entry(frame, textvariable=self.lyric_vars[key], width=40)
            entry.grid(row=idx, column=1, padx=8, pady=6, sticky="ew")
            self.lyric_entries[key] = entry
        frame.columnconfigure(1, weight=1)

    def build_icons_tab(self):
        frame = ttk.Frame(self.notebook, style="Card.TFrame", padding=12)
        self.notebook.add(frame, text="图标")
        self.tab_frames["图标"] = frame

        self.icons_dark_var = tk.BooleanVar()
        self.icons_path_var = tk.StringVar()
        self.icons_path_var.trace_add("write", lambda *_: self.load_icon_tree())

        ttk.Checkbutton(frame, text="深色模式", variable=self.icons_dark_var).grid(
            row=0, column=0, padx=8, pady=6, sticky="w"
        )
        ttk.Label(frame, text="路径").grid(row=0, column=1, padx=8, pady=6, sticky="w")
        ttk.Entry(frame, textvariable=self.icons_path_var, width=30).grid(
            row=0, column=2, padx=8, pady=6, sticky="ew"
        )

        actions = ttk.Frame(frame)
        actions.grid(row=1, column=0, columnspan=3, padx=8, pady=6, sticky="w")
        ttk.Button(actions, text="导入图标集", command=self.import_icons).pack(side="left", padx=4)
        ttk.Button(actions, text="选择图片", command=self.select_icon_image).pack(side="left", padx=4)
        ttk.Button(actions, text="清除图标", command=self.clear_icon_image).pack(side="left", padx=4)
        ttk.Button(actions, text="刷新列表", command=self.load_icon_tree).pack(side="left", padx=4)

        self.icons_status = tk.StringVar(value="")
        ttk.Label(frame, textvariable=self.icons_status).grid(
            row=2, column=0, columnspan=3, padx=8, pady=4, sticky="w"
        )

        self.icon_tree = self.make_tree(frame, ["图标ID", "文件"])
        self.icon_tree.grid(row=3, column=0, columnspan=3, padx=8, pady=6, sticky="nsew")
        self.icon_tree.bind("<Double-1>", lambda _e: self.select_icon_image())

        frame.columnconfigure(2, weight=1)
        frame.rowconfigure(3, weight=1)

    def build_assets_tab(self):
        frame = ttk.Frame(self.notebook, style="Card.TFrame", padding=12)
        self.notebook.add(frame, text="资源路径")
        self.tab_frames["资源路径"] = frame
        self.assets_base_var = tk.StringVar()
        self.assets_images_var = tk.StringVar()
        self.assets_buttons_var = tk.StringVar()

        fields = [
            ("根路径", self.assets_base_var),
            ("图片", self.assets_images_var),
            ("按钮", self.assets_buttons_var),
        ]
        for idx, (label, var) in enumerate(fields):
            ttk.Label(frame, text=label).grid(row=idx, column=0, padx=8, pady=6, sticky="w")
            ttk.Entry(frame, textvariable=var, width=40).grid(
                row=idx, column=1, padx=8, pady=6, sticky="ew"
            )
        frame.columnconfigure(1, weight=1)


    def build_preview_panel(self, parent):
        card = tk.Frame(
            parent,
            bg=UI_PALETTE["card"],
            highlightthickness=1,
            highlightbackground=UI_PALETTE["border"],
        )
        card.pack(fill="both", expand=True)

        header = tk.Frame(card, bg=UI_PALETTE["card"])
        header.pack(fill="x", padx=12, pady=10)
        tk.Label(header, text="预览", bg=UI_PALETTE["card"], fg=UI_PALETTE["text"]).pack(side="left")
        ttk.Button(header, text="刷新预览", command=self.refresh_preview).pack(side="right")

        self.preview_canvas = tk.Canvas(
            card,
            width=280,
            height=420,
            highlightthickness=0,
            bg=UI_PALETTE["card"],
        )
        self.preview_canvas.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.preview_canvas.bind("<Motion>", self.on_preview_hover)
        self.preview_canvas.bind("<Leave>", self.on_preview_leave)
        self.preview_canvas.bind("<Button-1>", self.on_preview_click)

        status = tk.Label(
            card,
            textvariable=self.preview_status_var,
            bg=UI_PALETTE["card"],
            fg=UI_PALETTE["muted"],
            anchor="w",
        )
        status.pack(fill="x", padx=12, pady=(0, 10))

    def resolve_asset_path(self, value):
        if not value:
            return None
        if os.path.isabs(value):
            return value
        if not self.project_dir:
            return None
        return os.path.join(self.project_dir, value)

    def load_preview_image(self, path, width, height):
        if not path:
            return None
        if not os.path.exists(path):
            return None
        if not path.lower().endswith(".png"):
            return None
        try:
            image = tk.PhotoImage(file=path)
        except Exception:
            return None
        iw, ih = image.width(), image.height()
        if iw <= 0 or ih <= 0:
            return None
        scale = max(iw / width, ih / height)
        if scale > 1:
            factor = int(scale)
            if factor > 1:
                image = image.subsample(factor, factor)
        return image

    def refresh_preview(self):
        if not hasattr(self, "preview_canvas"):
            return
        self.apply_ui_to_theme()
        data = self.theme_data
        canvas = self.preview_canvas
        canvas.delete("all")
        self.preview_tags = []

        width = max(canvas.winfo_width(), int(canvas["width"]))
        height = max(canvas.winfo_height(), int(canvas["height"]))

        colors = data.get("colors", {})
        backgrounds = data.get("backgrounds", {})
        bg_color = parse_color(colors.get("background"), "#f0f0f0")
        bg = backgrounds.get("app", {})
        bg_value = bg.get("value") or bg_color
        self.add_preview_tag(0, 0, width, height, "backgrounds.app", bg_value)

        drew_image = False
        if bg.get("type") == "image":
            image_path = self.resolve_asset_path(bg.get("value"))
            image = self.load_preview_image(image_path, width, height)
            if image:
                self.preview_image = image
                canvas.create_image(0, 0, anchor="nw", image=image)
                drew_image = True
        if not drew_image:
            if bg.get("type") == "color":
                bg_color = parse_color(bg.get("value"), bg_color)
            canvas.create_rectangle(0, 0, width, height, fill=bg_color, outline="")
            self.preview_image = None

        theme_color = parse_color(colors.get("theme"), "#00E5FF")
        text_primary = parse_color(colors.get("text_primary"), "#000000")
        text_secondary = parse_color(colors.get("text_secondary"), "#666666")

        text_cfg = data.get("text", {})
        title_color = parse_color(text_cfg.get("title"), text_primary)
        body_color = parse_color(text_cfg.get("body"), text_primary)
        caption_color = parse_color(text_cfg.get("caption"), text_secondary)

        header_h = 36
        canvas.create_rectangle(0, 0, width, header_h, fill=theme_color, outline="")
        self.add_preview_tag(0, 0, width, header_h, "colors.theme", colors.get("theme", theme_color))
        title = data.get("name") or "主题预览"
        canvas.create_text(10, header_h / 2, text=title, anchor="w", fill=text_primary)
        self.add_preview_tag(10, 0, 10 + 160, header_h, "colors.text_primary", colors.get("text_primary", text_primary))

        card = backgrounds.get("card", {})
        card_color = parse_color(colors.get("background"), "#ffffff")
        if card.get("type") == "color":
            card_color = parse_color(card.get("value"), card_color)

        card_x = 14
        card_y = header_h + 12
        card_w = width - 28
        card_h = 90
        canvas.create_rectangle(card_x, card_y, card_x + card_w, card_y + card_h, fill=card_color, outline="")
        self.add_preview_tag(
            card_x,
            card_y,
            card_x + card_w,
            card_y + card_h,
            "backgrounds.card",
            card.get("value", card_color),
        )
        canvas.create_text(card_x + 10, card_y + 12, text="标题", anchor="nw", fill=title_color)
        canvas.create_text(card_x + 10, card_y + 36, text="正文文本", anchor="nw", fill=body_color)
        canvas.create_text(card_x + 10, card_y + 60, text="说明文本", anchor="nw", fill=caption_color)
        self.add_preview_tag(card_x + 10, card_y + 8, card_x + 120, card_y + 26, "text.title", text_cfg.get("title"))
        self.add_preview_tag(card_x + 10, card_y + 32, card_x + 140, card_y + 50, "text.body", text_cfg.get("body"))
        self.add_preview_tag(
            card_x + 10, card_y + 56, card_x + 140, card_y + 74, "text.caption", text_cfg.get("caption")
        )

        btn_y = card_y + card_h + 16
        btn_h = 28
        btn_w = (width - 36) // 2
        primary = data.get("buttons", {}).get("primary", {})
        danger = data.get("buttons", {}).get("danger", {})
        primary_bg = parse_color(primary.get("bg"), theme_color)
        primary_text = parse_color(primary.get("text"), text_primary)
        danger_bg = parse_color(danger.get("bg"), "#FF3B30")
        danger_text = parse_color(danger.get("text"), "#FF3B30")

        canvas.create_rectangle(card_x, btn_y, card_x + btn_w, btn_y + btn_h, fill=primary_bg, outline="")
        canvas.create_text(card_x + btn_w / 2, btn_y + btn_h / 2, text="主按钮", fill=primary_text)
        self.add_preview_tag(
            card_x, btn_y, card_x + btn_w, btn_y + btn_h, "buttons.primary.bg", primary.get("bg")
        )
        self.add_preview_tag(
            card_x,
            btn_y,
            card_x + btn_w,
            btn_y + btn_h,
            "buttons.primary.text",
            primary.get("text"),
        )
        canvas.create_rectangle(
            card_x + btn_w + 8,
            btn_y,
            card_x + btn_w + 8 + btn_w,
            btn_y + btn_h,
            fill=danger_bg,
            outline="",
        )
        canvas.create_text(
            card_x + btn_w + 8 + btn_w / 2,
            btn_y + btn_h / 2,
            text="危险",
            fill=danger_text,
        )
        self.add_preview_tag(
            card_x + btn_w + 8,
            btn_y,
            card_x + btn_w + 8 + btn_w,
            btn_y + btn_h,
            "buttons.danger.bg",
            danger.get("bg"),
        )
        self.add_preview_tag(
            card_x + btn_w + 8,
            btn_y,
            card_x + btn_w + 8 + btn_w,
            btn_y + btn_h,
            "buttons.danger.text",
            danger.get("text"),
        )

        slider_y = btn_y + btn_h + 18
        slider_x1 = card_x
        slider_x2 = width - card_x
        slider_un = parse_color(colors.get("slider_unselected"), "#cccccc")
        slider_sel = parse_color(colors.get("slider_selected"), theme_color)
        canvas.create_rectangle(slider_x1, slider_y, slider_x2, slider_y + 6, fill=slider_un, outline="")
        canvas.create_rectangle(
            slider_x1,
            slider_y,
            slider_x1 + int((slider_x2 - slider_x1) * 0.6),
            slider_y + 6,
            fill=slider_sel,
            outline="",
        )
        self.add_preview_tag(
            slider_x1, slider_y, slider_x2, slider_y + 6, "colors.slider_unselected", colors.get("slider_unselected")
        )
        self.add_preview_tag(
            slider_x1,
            slider_y,
            slider_x1 + int((slider_x2 - slider_x1) * 0.6),
            slider_y + 6,
            "colors.slider_selected",
            colors.get("slider_selected"),
        )

        lyric_cfg = data.get("lyric", {})
        lyric_active = parse_color(lyric_cfg.get("active"), theme_color)
        lyric_normal = parse_color(lyric_cfg.get("normal"), text_secondary)
        lyric_y = slider_y + 18
        canvas.create_text(card_x, lyric_y, text="歌词高亮", anchor="nw", fill=lyric_active)
        canvas.create_text(card_x, lyric_y + 20, text="歌词普通", anchor="nw", fill=lyric_normal)
        self.add_preview_tag(card_x, lyric_y, card_x + 120, lyric_y + 16, "lyric.active", lyric_cfg.get("active"))
        self.add_preview_tag(
            card_x, lyric_y + 20, card_x + 120, lyric_y + 36, "lyric.normal", lyric_cfg.get("normal")
        )

    def add_preview_tag(self, x1, y1, x2, y2, field, value):
        self.preview_tags.append((x1, y1, x2, y2, field, value))

    def get_preview_tag_at(self, x, y):
        for x1, y1, x2, y2, field, value in reversed(self.preview_tags):
            if x1 <= x <= x2 and y1 <= y <= y2:
                return field, value
        return None

    def on_preview_hover(self, event):
        tag = self.get_preview_tag_at(event.x, event.y)
        if not tag:
            if self.preview_hover_key is not None:
                self.preview_status_var.set("")
                self.preview_canvas.configure(cursor="")
                self.preview_hover_key = None
            return
        field, value = tag
        key = f"{field}:{value}"
        if key != self.preview_hover_key:
            display = value if value not in (None, "") else "-"
            self.preview_status_var.set(f"{field}: {display} (点击编辑)")
            self.preview_canvas.configure(cursor="hand2")
            self.preview_hover_key = key

    def on_preview_leave(self, _event):
        self.preview_status_var.set("")
        self.preview_canvas.configure(cursor="")
        self.preview_hover_key = None

    def on_preview_click(self, event):
        tag = self.get_preview_tag_at(event.x, event.y)
        if not tag:
            return
        field, _value = tag
        self.jump_to_field(field)

    def jump_to_field(self, field):
        prefix, _, name = field.partition(".")
        key = name.split(".")[0] if name else ""
        if prefix == "colors":
            self.select_tab("颜色")
            self.select_tree_item(self.colors_tree, key)
        elif prefix == "text":
            self.select_tab("文字")
            self.select_tree_item(self.text_tree, key)
        elif prefix == "backgrounds":
            self.select_tab("背景")
            self.select_tree_item(self.backgrounds_tree, key)
        elif prefix == "buttons":
            self.select_tab("按钮")
            self.select_tree_item(self.buttons_tree, key)
        elif prefix == "lyric":
            self.select_tab("歌词")
            entry = self.lyric_entries.get(key)
            if entry:
                entry.focus_set()

    def select_tab(self, name):
        frame = self.tab_frames.get(name)
        if frame:
            self.notebook.select(frame)

    def select_tree_item(self, tree, key):
        if key in tree.get_children():
            tree.selection_set(key)
            tree.focus(key)
            tree.see(key)

    def make_tree(self, parent, columns):
        tree = ttk.Treeview(parent, columns=columns, show="headings", selectmode="browse")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor="w")
        return tree

    def add_tree_buttons(self, parent, tree, add_cmd, edit_cmd, remove_cmd):
        btns = ttk.Frame(parent)
        btns.pack(fill="x", padx=6, pady=4)
        ttk.Button(btns, text="添加", command=add_cmd).pack(side="left", padx=4)
        ttk.Button(btns, text="编辑", command=edit_cmd).pack(side="left", padx=4)
        ttk.Button(btns, text="删除", command=remove_cmd).pack(side="left", padx=4)

    def set_project(self, folder):
        self.project_dir = folder
        self.project_var.set(folder or "未加载项目")

    def load_theme_into_ui(self):
        data = normalize_theme(self.theme_data)
        self.id_var.set(data.get("id", ""))
        self.name_var.set(data.get("name", ""))
        self.desc_var.set(data.get("description", ""))
        self.version_var.set(data.get("version", ""))
        self.author_var.set(data.get("author", ""))
        self.min_app_var.set(str(data.get("minAppVersion", "")))
        self.min_platform_var.set(str(data.get("minPlatformVersion", "")))

        self.load_key_value_tree(self.colors_tree, data.get("colors", {}), required_keys=REQUIRED_COLOR_KEYS)
        self.load_key_value_tree(self.text_tree, data.get("text", {}))
        self.load_backgrounds_tree(data.get("backgrounds", {}))
        self.load_buttons_tree(data.get("buttons", {}))
        self.set_app_background_controls(data.get("backgrounds", {}))

        lyric = data.get("lyric", {})
        for key in self.lyric_vars:
            self.lyric_vars[key].set(lyric.get(key, ""))

        icons = data.get("icons", {})
        self.icons_dark_var.set(bool(icons.get("dark_mode", False)))
        self.icons_path_var.set(icons.get("path", "icons"))

        assets = data.get("assets", {})
        self.assets_base_var.set(assets.get("base", "."))
        self.assets_images_var.set(assets.get("images", "images"))
        self.assets_buttons_var.set(assets.get("buttons", "buttons"))

        self.update_icon_status()
        self.load_icon_tree()
        self.refresh_preview()

    def apply_ui_to_theme(self):
        data = dict(self.theme_data)
        self.sync_app_background_to_tree()
        data["schemaVersion"] = THEME_SCHEMA_VERSION
        data["id"] = self.id_var.get().strip()
        data["name"] = self.name_var.get().strip()
        data["description"] = self.desc_var.get().strip()
        data["version"] = self.version_var.get().strip()
        data["author"] = self.author_var.get().strip()
        data["minAppVersion"] = self.min_app_var.get().strip()
        min_platform = self.min_platform_var.get().strip()
        try:
            data["minPlatformVersion"] = int(min_platform)
        except ValueError:
            data["minPlatformVersion"] = 0

        data["colors"] = self.tree_to_key_value(self.colors_tree)
        data["text"] = self.tree_to_key_value(self.text_tree)
        data["backgrounds"] = self.tree_to_backgrounds(self.backgrounds_tree)
        data["buttons"] = self.tree_to_buttons(self.buttons_tree)
        data["lyric"] = {key: var.get().strip() for key, var in self.lyric_vars.items()}
        data["icons"] = {"dark_mode": bool(self.icons_dark_var.get()), "path": self.icons_path_var.get().strip()}
        data["assets"] = {
            "base": self.assets_base_var.get().strip(),
            "images": self.assets_images_var.get().strip(),
            "buttons": self.assets_buttons_var.get().strip(),
        }
        self.theme_data = normalize_theme(data)

    def load_key_value_tree(self, tree, data_dict, required_keys=None):
        tree.delete(*tree.get_children())
        required_keys = required_keys or []
        for key in required_keys:
            if key in data_dict:
                tree.insert("", "end", iid=key, values=(key, data_dict[key]))
            else:
                tree.insert("", "end", iid=key, values=(key, DEFAULT_COLORS.get(key, "")))
        for key in sorted(data_dict.keys()):
            if key in required_keys:
                continue
            tree.insert("", "end", iid=key, values=(key, data_dict[key]))

    def load_backgrounds_tree(self, data_dict):
        self.backgrounds_tree.delete(*self.backgrounds_tree.get_children())
        for key in sorted(data_dict.keys()):
            item = data_dict[key] or {}
            self.backgrounds_tree.insert(
                "",
                "end",
                iid=key,
                values=(
                    key,
                    item.get("type", ""),
                    item.get("value", ""),
                    item.get("objectFit", ""),
                ),
            )

    def set_app_background_controls(self, backgrounds):
        if not hasattr(self, "app_bg_type_var"):
            return
        app = backgrounds.get("app", {})
        self.app_bg_type_var.set(app.get("type", "color"))
        self.app_bg_value_var.set(app.get("value", ""))

    def browse_app_background(self):
        if not self.project_dir:
            messagebox.showerror("未打开主题", "请先新建或打开主题。")
            return
        src = filedialog.askopenfilename(
            title="选择背景图片",
            filetypes=[("图片文件", "*.png;*.jpg;*.jpeg;*.webp"), ("所有文件", "*.*")],
        )
        if not src:
            return
        rel = copy_into_project(self.project_dir, src, "images")
        self.app_bg_value_var.set(rel)
        self.app_bg_type_var.set("image")

    def sync_app_background_to_tree(self):
        if not hasattr(self, "backgrounds_tree"):
            return
        key = "app"
        typ = self.app_bg_type_var.get().strip() or "color"
        value = self.app_bg_value_var.get().strip()
        obj_fit = ""
        if key in self.backgrounds_tree.get_children():
            self.backgrounds_tree.item(key, values=(key, typ, value, obj_fit))
        else:
            self.backgrounds_tree.insert("", "end", iid=key, values=(key, typ, value, obj_fit))

    def apply_app_background(self):
        self.sync_app_background_to_tree()
        self.refresh_preview()

    def get_icons_dir(self):
        if not self.project_dir:
            return None
        path = self.icons_path_var.get().strip() or "icons"
        if ".." in path:
            return None
        return os.path.join(self.project_dir, path)

    def load_buttons_tree(self, data_dict):
        self.buttons_tree.delete(*self.buttons_tree.get_children())
        for key in sorted(data_dict.keys()):
            item = data_dict[key] or {}
            self.buttons_tree.insert(
                "",
                "end",
                iid=key,
                values=(
                    key,
                    item.get("bg", ""),
                    item.get("text", ""),
                    item.get("border", ""),
                    item.get("image", ""),
                ),
            )


    def tree_to_key_value(self, tree):
        data = {}
        for iid in tree.get_children():
            key, value = tree.item(iid, "values")
            data[key] = value
        return data

    def tree_to_backgrounds(self, tree):
        data = {}
        for iid in tree.get_children():
            key, typ, value, obj_fit = tree.item(iid, "values")
            entry = {"type": typ, "value": value}
            if obj_fit:
                entry["objectFit"] = obj_fit
            data[key] = entry
        return data

    def tree_to_buttons(self, tree):
        data = {}
        for iid in tree.get_children():
            key, bg, text, border, image = tree.item(iid, "values")
            entry = {"bg": bg, "text": text}
            if border:
                entry["border"] = border
            if image:
                entry["image"] = image
            data[key] = entry
        return data

    def new_project(self):
        base = filedialog.askdirectory(title="选择保存目录")
        if not base:
            return
        theme_id = simpledialog.askstring("主题 ID", "请输入主题 ID（小写字母/数字/下划线）：")
        if not theme_id:
            return
        if not validate_id(theme_id):
            messagebox.showerror("ID 无效", "主题 ID 只能包含小写字母、数字和下划线。")
            return
        folder = os.path.join(base, theme_id)
        ensure_dir(folder)
        ensure_dir(os.path.join(folder, "icons"))
        ensure_dir(os.path.join(folder, "images"))
        ensure_dir(os.path.join(folder, "buttons"))
        self.theme_data = default_theme(theme_id)
        self.set_project(folder)
        self.save_project()
        self.load_theme_into_ui()

    def open_project(self):
        folder = filedialog.askdirectory(title="打开主题文件夹")
        if not folder:
            return
        theme_path = os.path.join(folder, "theme.json")
        if not os.path.exists(theme_path):
            messagebox.showerror("缺少 theme.json", "所选文件夹不包含 theme.json。")
            return
        try:
            self.theme_data = normalize_theme(read_json(theme_path))
        except Exception as exc:
            messagebox.showerror("加载失败", f"加载 theme.json 出错：{exc}")
            return
        self.set_project(folder)
        self.load_theme_into_ui()

    def save_project(self):
        if not self.project_dir:
            messagebox.showerror("未打开主题", "请先新建或打开主题。")
            return
        self.apply_ui_to_theme()
        theme_id = self.theme_data.get("id", "")
        if not validate_id(theme_id):
            messagebox.showerror("ID 无效", "主题 ID 只能包含小写字母、数字和下划线。")
            return
        warnings = validate_paths(self.theme_data)
        if warnings:
            messagebox.showwarning("路径警告", "\n".join(warnings))
        theme_path = os.path.join(self.project_dir, "theme.json")
        output = build_theme_output(self.theme_data)
        write_json(theme_path, output)
        self.update_icon_status()
        self.refresh_preview()
        messagebox.showinfo("已保存", "主题保存成功。")

    def export_zip(self):
        if not self.project_dir:
            messagebox.showerror("未打开主题", "请先新建或打开主题。")
            return
        self.save_project()
        theme_id = self.theme_data.get("id", "theme")
        default_name = f"{theme_id}.zip"
        output = filedialog.asksaveasfilename(
            title="导出压缩包", defaultextension=".zip", initialfile=default_name
        )
        if not output:
            return
        root_name = theme_id
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _dirs, files in os.walk(self.project_dir):
                rel_root = os.path.relpath(root, self.project_dir)
                for filename in files:
                    if filename == "image_map.json":
                        continue
                    if filename.startswith("."):
                        continue
                    src = os.path.join(root, filename)
                    if rel_root == ".":
                        arcname = os.path.join(root_name, filename)
                    else:
                        arcname = os.path.join(root_name, rel_root, filename)
                    zf.write(src, arcname)
        messagebox.showinfo("已导出", f"压缩包已导出：{output}")

    def add_color(self):
        dlg = KeyValueDialog(self.root, "添加颜色")
        self.root.wait_window(dlg)
        if not dlg.result:
            return
        key, value = dlg.result
        if key in self.colors_tree.get_children():
            messagebox.showerror("键重复", "该键已存在。")
            return
        self.colors_tree.insert("", "end", iid=key, values=(key, value))
        self.refresh_preview()

    def edit_color(self):
        item = self.get_selected(self.colors_tree)
        if not item:
            return
        key, value = self.colors_tree.item(item, "values")
        dlg = KeyValueDialog(self.root, "编辑颜色", key=key, value=value, readonly_key=key in REQUIRED_COLOR_KEYS)
        self.root.wait_window(dlg)
        if not dlg.result:
            return
        new_key, new_value = dlg.result
        if new_key != key and new_key in self.colors_tree.get_children():
            messagebox.showerror("键重复", "该键已存在。")
            return
        self.colors_tree.delete(item)
        self.colors_tree.insert("", "end", iid=new_key, values=(new_key, new_value))
        self.refresh_preview()

    def remove_color(self):
        item = self.get_selected(self.colors_tree)
        if not item:
            return
        key = self.colors_tree.item(item, "values")[0]
        if key in REQUIRED_COLOR_KEYS:
            messagebox.showerror("必填", "该颜色为必填，不能删除。")
            return
        self.colors_tree.delete(item)
        self.refresh_preview()

    def add_text(self):
        dlg = KeyValueDialog(self.root, "添加文字")
        self.root.wait_window(dlg)
        if not dlg.result:
            return
        key, value = dlg.result
        if key in self.text_tree.get_children():
            messagebox.showerror("键重复", "该键已存在。")
            return
        self.text_tree.insert("", "end", iid=key, values=(key, value))
        self.refresh_preview()

    def edit_text(self):
        item = self.get_selected(self.text_tree)
        if not item:
            return
        key, value = self.text_tree.item(item, "values")
        dlg = KeyValueDialog(self.root, "编辑文字", key=key, value=value)
        self.root.wait_window(dlg)
        if not dlg.result:
            return
        new_key, new_value = dlg.result
        if new_key != key and new_key in self.text_tree.get_children():
            messagebox.showerror("键重复", "该键已存在。")
            return
        self.text_tree.delete(item)
        self.text_tree.insert("", "end", iid=new_key, values=(new_key, new_value))
        self.refresh_preview()

    def remove_text(self):
        item = self.get_selected(self.text_tree)
        if not item:
            return
        self.text_tree.delete(item)
        self.refresh_preview()

    def add_background(self):
        dlg = BackgroundDialog(self.root, "添加背景", {}, self.project_dir)
        self.root.wait_window(dlg)
        if not dlg.result:
            return
        key = dlg.result["key"]
        if key in self.backgrounds_tree.get_children():
            messagebox.showerror("键重复", "该键已存在。")
            return
        self.backgrounds_tree.insert(
            "", "end", iid=key, values=(key, dlg.result["type"], dlg.result["value"], dlg.result["objectFit"])
        )
        self.refresh_preview()

    def edit_background(self):
        item = self.get_selected(self.backgrounds_tree)
        if not item:
            return
        values = self.backgrounds_tree.item(item, "values")
        data = {"key": values[0], "type": values[1], "value": values[2], "objectFit": values[3]}
        dlg = BackgroundDialog(self.root, "编辑背景", data, self.project_dir)
        self.root.wait_window(dlg)
        if not dlg.result:
            return
        key = dlg.result["key"]
        if key != values[0] and key in self.backgrounds_tree.get_children():
            messagebox.showerror("键重复", "该键已存在。")
            return
        self.backgrounds_tree.delete(item)
        self.backgrounds_tree.insert(
            "", "end", iid=key, values=(key, dlg.result["type"], dlg.result["value"], dlg.result["objectFit"])
        )
        self.refresh_preview()

    def remove_background(self):
        item = self.get_selected(self.backgrounds_tree)
        if not item:
            return
        self.backgrounds_tree.delete(item)
        self.refresh_preview()

    def add_button(self):
        dlg = ButtonDialog(self.root, "添加按钮", {}, self.project_dir)
        self.root.wait_window(dlg)
        if not dlg.result:
            return
        key = dlg.result["key"]
        if key in self.buttons_tree.get_children():
            messagebox.showerror("键重复", "该键已存在。")
            return
        self.buttons_tree.insert(
            "",
            "end",
            iid=key,
            values=(key, dlg.result["bg"], dlg.result["text"], dlg.result["border"], dlg.result["image"]),
        )
        self.refresh_preview()

    def edit_button(self):
        item = self.get_selected(self.buttons_tree)
        if not item:
            return
        values = self.buttons_tree.item(item, "values")
        data = {"key": values[0], "bg": values[1], "text": values[2], "border": values[3], "image": values[4]}
        dlg = ButtonDialog(self.root, "编辑按钮", data, self.project_dir)
        self.root.wait_window(dlg)
        if not dlg.result:
            return
        key = dlg.result["key"]
        if key != values[0] and key in self.buttons_tree.get_children():
            messagebox.showerror("键重复", "该键已存在。")
            return
        self.buttons_tree.delete(item)
        self.buttons_tree.insert(
            "",
            "end",
            iid=key,
            values=(key, dlg.result["bg"], dlg.result["text"], dlg.result["border"], dlg.result["image"]),
        )
        self.refresh_preview()

    def remove_button(self):
        item = self.get_selected(self.buttons_tree)
        if not item:
            return
        self.buttons_tree.delete(item)
        self.refresh_preview()

    def get_selected(self, tree):
        sel = tree.selection()
        if not sel:
            messagebox.showerror("未选择", "请先选择一项。")
            return None
        return sel[0]

    def import_icons(self):
        if not self.project_dir:
            messagebox.showerror("未打开主题", "请先新建或打开主题。")
            return
        src_dir = filedialog.askdirectory(title="选择图标文件夹")
        if not src_dir:
            return
        icons_dir = self.get_icons_dir()
        if not icons_dir:
            messagebox.showerror("路径无效", "图标路径无效。")
            return
        ensure_dir(icons_dir)
        copied = 0
        for name in REQUIRED_ICON_NAMES:
            src = os.path.join(src_dir, name)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(icons_dir, name))
                copied += 1
        missing = list_missing_icons(icons_dir)
        if missing:
            self.icons_status.set(f"缺少 {len(missing)} 个图标")
            messagebox.showwarning("图标缺失", f"缺少图标：{', '.join(missing)}")
        else:
            self.icons_status.set("图标齐全")
        if copied == 0:
            messagebox.showinfo("未复制图标", "未找到匹配的图标文件。")
        self.load_icon_tree()

    def update_icon_status(self):
        if not self.project_dir:
            self.icons_status.set("")
            return
        icons_dir = self.get_icons_dir()
        if not icons_dir:
            self.icons_status.set("图标路径无效")
            return
        if not os.path.exists(icons_dir):
            self.icons_status.set("图标文件夹不存在")
            return
        missing = list_missing_icons(icons_dir)
        if missing:
            self.icons_status.set(f"缺少 {len(missing)} 个图标")
        else:
            self.icons_status.set("图标齐全")

    def load_icon_tree(self):
        if not hasattr(self, "icon_tree"):
            return
        self.icon_tree.delete(*self.icon_tree.get_children())
        icons_dir = None
        if self.project_dir:
            icons_dir = self.get_icons_dir()
        for name in REQUIRED_ICON_NAMES:
            rel = ""
            if icons_dir:
                path = os.path.join(icons_dir, name)
                if os.path.exists(path):
                    rel = rel_path(os.path.relpath(path, self.project_dir))
            self.icon_tree.insert("", "end", iid=name, values=(name, rel))

    def select_icon_image(self):
        if not self.project_dir:
            messagebox.showerror("未打开主题", "请先新建或打开主题。")
            return
        item = self.get_selected(self.icon_tree)
        if not item:
            return
        src = filedialog.askopenfilename(
            title="选择图标图片",
            filetypes=[("图片文件", "*.png;*.jpg;*.jpeg;*.webp"), ("所有文件", "*.*")],
        )
        if not src:
            return
        icons_dir = self.get_icons_dir()
        if not icons_dir:
            messagebox.showerror("路径无效", "图标路径无效。")
            return
        ensure_dir(icons_dir)
        dest = os.path.join(icons_dir, item)
        shutil.copy2(src, dest)
        rel = rel_path(os.path.relpath(dest, self.project_dir))
        self.icon_tree.item(item, values=(item, rel))
        self.update_icon_status()

    def clear_icon_image(self):
        if not self.project_dir:
            messagebox.showerror("未打开主题", "请先新建或打开主题。")
            return
        item = self.get_selected(self.icon_tree)
        if not item:
            return
        icons_dir = self.get_icons_dir()
        if not icons_dir:
            messagebox.showerror("路径无效", "图标路径无效。")
            return
        path = os.path.join(icons_dir, item)
        if os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                messagebox.showerror("删除失败", "无法删除该图标文件。")
                return
        self.icon_tree.item(item, values=(item, ""))
        self.update_icon_status()


def main():
    root = tk.Tk()
    apply_modern_theme(root)
    app = ThemeToolApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
