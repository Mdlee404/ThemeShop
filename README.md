# 氦音乐主题商店（Cloudflare Pages）

一个可部署在 **Cloudflare Pages** 的静态前端项目：

- 在仓库 `packages/` 上传主题 ZIP 包
- 通过 GitHub Actions 自动解压、读取 `theme.json`、生成统一索引
- 前端展示主题列表、预览图、作者、描述
- 详情页支持下载、预览切换、查看原始 `theme.json`
- 内置 Web 版主题制作工具（浏览器直接生成 JSON / ZIP）
- 提供 JS 参考工具（初始化/校验/打包）

---

## 目录结构

```txt
.
├─ .github/workflows/sync-theme-catalog.yml
├─ packages/                     # 主题 zip 上传目录
├─ scripts/build-theme-index.mjs # Node/JS 自动解压 + 索引生成脚本
├─ index.html                    # 主题商店首页（根目录可直接访问）
├─ theme.html                    # 主题详情页
├─ builder.html                  # Web 主题制作工具
├─ data/themes.json              # 自动生成主题索引
├─ themes/                       # 自动解压后的主题目录
├─ downloads/                    # 原始 zip 可下载文件
└─ assets/                       # JS / CSS / SVG icon
└─ tools/theme-builder-reference.mjs
```

---

## 本地构建

```bash
npm ci
npm run build:data
npm run verify:site
```

执行后会：

1. 扫描 `packages/*.zip`
2. 解压到 `themes/<themeId>/`
3. 复制 ZIP 到 `downloads/`
4. 生成 `data/themes.json`

---

## GitHub Actions 自动化

工作流：`.github/workflows/sync-theme-catalog.yml`

触发条件：

- push 到 `main` 且涉及 `packages/*.zip` 或构建脚本
- 手动触发 `workflow_dispatch`

行为：

- 运行 `npm run build:data`
- 若生成文件有变更，自动提交回仓库

---

## Cloudflare Pages 部署

在 Cloudflare Pages 新建项目并连接 GitHub 仓库：

- **Framework preset**: `None`
- **Build command**: `npm ci && npm run build:data`
- **Build output directory**: `.`

这样部署后，访问站点根 URL 就能直接打开 `index.html`，不会再出现“找不到网页入口/样式失效”。

---

## 主题 ZIP 规范

建议每个 ZIP 内部为：

```txt
{themeId}/
  theme.json
  preview.png
  icons/
  images/
  buttons/
```

解析逻辑兼容：

- 有单一根目录（如 `autumn_firefly/`）
- 或文件直接位于 ZIP 根目录

`theme.json` 至少应包含：

- `id`
- `name`
- `version`
- `author`
- `description`
- `colors`（含必要字段）

---

## 前端功能清单

- 现代简洁 UI，移动端优先 + PC 舒适布局
- 大量 SVG 图标（无外链图标依赖）
- 线性旋转 + 非线性浮动背景动画
- 日间/夜间模式切换并持久化偏好
- 首页搜索、统计卡片、主题列表卡片
- 详情页多图预览、下载按钮、JSON 查看
- Web 主题制作工具（实时预览 + 导出 JSON + 直接打包 ZIP）
- 页面资源全部相对路径，兼容 Pages 根路径/子路径访问

---

## Web 工具直接打包 ZIP

页面：`/builder.html`

- 点击“下载 ZIP 主题包”即可导出 `{themeId}.zip`
- ZIP 至少包含：`{themeId}/theme.json`
- 可选附带：
  - `preview.*`
  - `images/bg_app.*`
  - `buttons/primary.*`
  - `buttons/danger.*`

导出的 ZIP 可直接放进仓库 `packages/`，交由 Actions 自动处理。

---

## Python 参考工具（CLI）
## JS 参考工具（CLI）

文件：`tools/theme-builder-reference.mjs`

### 1) 初始化主题目录

```bash
node tools/theme-builder-reference.mjs init --id aurora --name 极光 --author Mindrift
```

### 2) 校验 theme.json

```bash
node tools/theme-builder-reference.mjs validate --file ./aurora/theme.json
```

### 3) 打包为 zip

```bash
node tools/theme-builder-reference.mjs pack --dir ./aurora --out ./packages/aurora.zip
```

---

## 可维护性与扩展建议

- 前端按模块拆分：`catalog.js`、`theme.js`、`icons.js`
- 构建逻辑集中在 `scripts/build-theme-index.mjs`
- 主题元数据统一来源：`data/themes.json`
- 后续可新增：
  - 主题评分/排序字段
  - 分类与筛选器（明暗风格、色系）
  - 可视化校验报告
  - 与发布标签/Release 联动
