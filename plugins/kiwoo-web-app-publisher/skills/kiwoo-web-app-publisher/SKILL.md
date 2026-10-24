---
name: kiwoo-web-app-publisher
description: 当用户需要把一个纯前端项目或一段静态页面，通过 Kiwoo（原 Loot）部署令牌预览并部署为「我的创作」里的作品（一键部署 / 安装口令；用户可能说「部署到 Kiwoo」或「部署到 Loot」）。
display_name: "Kiwoo Web App Publisher"
display_name_en: "Kiwoo Web App Publisher"
description_zh: "在预览确认后，把纯前端单文件 HTML 发布到 Kiwoo 草稿箱。"
description_en: "Preview and publish a pure-frontend single-file HTML app to Kiwoo Drafts after explicit confirmation."
version: "1.1.1"
author: "Kiwoo Lab"
---

# Kiwoo 一键部署（单文件 HTML）

Kiwoo 一键部署把**一个纯前端项目**或**一段静态页面**打包成单 HTML 入口，
经 Kiwoo 部署接口签发 10 分钟预览链接供用户检查。只有用户在检查后用当前对话语言明确表达
预览无误并确认发布，才保存到 Kiwoo 草稿箱。
这里的「发布」只表示进入用户自己的草稿箱，作品仍是草稿，**不会公开上线**。
用户在个人中心复制的安装口令，指向的就是本技能。

本技能只处理**纯前端**产物，最终交付物永远是**一个完整的 HTML 文件**。应用自己的 JS/CSS
应内联或打包进 HTML；浏览器运行时依赖可以使用 Kiwoo 托管资源或用户明确需要的公开 HTTPS
资源。单文件是部署接口的输入格式，**不代表作品必须离线运行**。部署使用**部署令牌
（Deploy Token）**鉴权，与网站登录态无关；每个用户有唯一的部署令牌，可在个人中心随时查看
或轮换。

禁止把真实部署令牌复制进本技能目录或提交记录。

## 保留用户要求的能力

单 HTML、纯前端和无密钥是**部署验收条件**，不是修改产品需求的授权。先识别用户明确要求的核心
能力（例如摄像头手势、语音、多人交互或外部数据），生成、改造和预览后的作品都必须保留这些能力；
不要为了通过部署质检而自行删除、替换或弱化它们。

- 优先寻找在单 HTML 中保留能力的实现，例如浏览器原生 API、Kiwoo 托管运行时、可内联依赖或等价
  的纯前端实现。摄像头、MediaPipe、WASM 或模型依赖先读
  [references/runtime-assets.md](references/runtime-assets.md)。鼠标、触摸、键盘等备用交互可以作为
  补充，但不能未经确认替代用户指定的主要交互。
- 如果核心能力没有可用的纯前端实现、超过 HTML 大小上限、需要服务端或密钥，必须在继续实现前
  说明具体阻碍、已核实的事实和可选方案，等待用户选择。未经确认，不得生成或部署删减版。
- 不要用按钮占位、模拟结果、静默 fallback，或在页面里加入 `alert()` / 提示文案来事后解释功能
  已被移除。这些都不等于实现了用户要求。
- 只有用户明确同意改变功能范围后，才能制作相应的降级版本；在交付说明中记录这个选择。

## 建立 Kiwoo 对象点选契约

在生成或改造包含可独立编辑视觉概念的作品前，完整读取
[references/scene-authoring.md](references/scene-authoring.md)。该文件由 Kiwoo 的权威
Scene Manifest schema 自动生成；不要在这里复制或猜测 Manifest、SourceBinding、
`registerNode` 或 adapter 字段。

- 由你根据产品语义决定稳定 semantic owner；不要按关键词套节点，也不要为每个粒子、实例或
  landmark 制造节点。重复 primitive 使用 aggregate/layer 或有界 proxy。
- 持久化 HTML 必须包含静态完整的 `loot_scene_authoring.v5` Manifest；运行时代码只把稳定
  `node_id` 绑定到真实 `runtime_ref`，并安装与 DOM、Canvas 或 Three.js 对应的 production adapter。
- 点选增强不得删减用户要求的摄像头、语音、动画、模型或数据能力，也不得阻塞普通 Preview 或保存草稿。
- 部署结果里的 `selection` 才是能力事实：只有 `capability=object_runtime_verified` 可以表述为
  “支持对象点选”；`object_declared` 表示静态契约已建立但运行时未验证；`region_only` 表示仅能圈选；
  `invalid` 表示声明或运行时证明需要修复。普通 HTTP 2xx、preview URL 或 `check.ok=true` 都不能替代它。
- Manifest JSON 截断、绑定非法或 runtime proof 不完整时显式报告，不自动补 JSON、不生成 seed Manifest，
  也不从普通 DOM id 或 Canvas 像素猜测 SourceBinding。

## 开始前

1. 确认用户要**改造已有纯前端项目**（场景 A）还是**新建一个静态页面**（场景 B），并确认
   应用目标、源项目目录（如有）和输出位置。
2. 说明最终交付一个通过质检的**单文件 HTML**；用户要求部署时，先交付 10 分钟预览链接并停下
   等待用户验证。交付时使用与用户请求相同的语言，请用户在预览无误后明确回复对应语言的确认语，
   并说明发布只会保存到 Kiwoo 草稿箱，不会公开上线。收到同时包含预览认可和发布授权的明确回复后，
   才保存草稿；是否公开由用户随后在 Kiwoo 工作台自行决定。
3. 先把本 `SKILL.md` 所在目录记为 `SKILL_DIR`。检查 `python3`（Windows 用 `py -3` 或
   `python`）、以及场景 A 需要的 `node`、`npm` 是否可用并输出版本。发布脚本要求
   **Python >= 3.8，零第三方依赖**（纯标准库，无需 `pip install`）。场景 A 的官方推荐构建
   工具为 Vite，需 Node.js。
4. 工具缺失或版本不兼容时，明确报告缺失项。安装或升级系统软件前先征得用户同意，禁止
   静默安装。

## 原项目只读，在项目内的副本工作

只要任务涉及用户已有项目或已有 HTML，原代码就视为只读。除了在原项目的 `.loot/` 下创建工作
副本和保存 Kiwoo 作品身份，不得直接修改原项目里的源码、配置、依赖清单、lockfile 或构建产物，
也不得在原项目目录直接安装依赖或运行会写文件的构建命令。

1. 把用户给出的目录记为 `ORIGINAL_PROJECT_DIR`。先读取其中适用的说明文件并盘点项目，但不编辑。
2. 用本技能提供的脚本在原项目内部创建一份新的、互相隔离的完整副本：

   ```bash
   python3 "$SKILL_DIR/scripts/prepare_project_copy.py" \
     --project-dir /path/to/original-project
   ```

   Windows PowerShell：

   ```powershell
   py -3 (Join-Path $SkillDir "scripts\prepare_project_copy.py") `
     --project-dir C:\path\to\original-project
   ```

3. 从脚本 JSON 输出读取 `workspace_dir`，记为 `WORKSPACE_DIR`。它位于
   `ORIGINAL_PROJECT_DIR/.loot/deploy-workspaces/workspace-*`，包含当前工作树（包括未提交修改）的
   副本，但不复制 `.git`、`.loot`、`node_modules`、`dist` 等依赖或生成目录。每次执行都会新建
   副本，不覆盖旧副本及其中的 Agent 修改。
4. 后续的源码编辑、配置调整、依赖安装、格式化、测试和 build **全部在 `WORKSPACE_DIR` 中执行**。
   不要把修改反向同步到原项目；只有用户随后明确要求时，才单独讨论如何应用这些改动。
5. 预览和发布时，`--html-file` 指向副本的单文件 build 产物，`--project-dir` 仍传
   `ORIGINAL_PROJECT_DIR`，让稳定的 `.loot/loot-artifact.json` 留在原项目根下。

## 只支持纯前端

部署接口只接受单文件 HTML。遇到以下情况必须先停下来向用户说明：

- 项目包含后端 / SSR / 服务端路由 / 数据库 / 服务端密钥：**不支持整体部署**。可与用户商量
  **只把纯前端部分**改造成独立单文件 HTML（去掉对自有后端的依赖，或指向用户已公开可访问的
  API），或明确告知无法部署。
- 页面运行时依赖脚本、样式、WASM 或模型：优先使用 Kiwoo 已托管的固定版本资源；其次才使用可靠的
  公开 HTTPS 资源并提供可见的失败状态。不要因为依赖不是内联的就删除对应功能。摄像头和常用
  MediaPipe 资源见 [references/runtime-assets.md](references/runtime-assets.md)。
- 需要把任何密钥 / 令牌写进前端才能工作：禁止把密钥内联进 HTML，向用户说明并改用无密钥方案。

判断当前项目无法整体部署，或用户要求的核心能力无法同时满足部署条件时，**不要静默降级、也不要
含糊带过**（例如只丢一个前端单文件却不解释为什么）。必须先在对话里给用户一段结构化说明，至少包含：

1. **不支持的原因**：逐条列出踩到的红线（后端 / SSR / 服务端路由 / 数据库 / 服务端鉴权 /
   多文件构建产物 / 依赖构建才能运行的源码 / 密钥依赖……），并说明 Kiwoo 只运行**单文件纯前端
   HTML**、在沙箱 iframe 里**纯客户端**渲染，因此当前项目**无法整体部署**为 Kiwoo 作品。
2. **能力影响**：明确指出哪些用户要求的能力会受影响；不得用「保证离线运行」笼统代替真实技术
   原因，也不得先做删减版再让用户接受既成事实。
3. **可选路径**：
   - A) 保留核心能力，使用 Kiwoo 托管运行时，或把所需依赖内联、压缩到大小上限内，再部署；
   - B) 抽取项目里的**纯前端交互部分**，但仅在用户明确同意功能变化后再改造和部署；
   - C) 按纯前端规范重新创建，或暂不部署到 Kiwoo。
4. **给出可直接复制的示例 prompt**，例如：
   - 「创建一个手势识别项目，按纯前端单文件 HTML 规范做，部署到 Kiwoo」
   - 「把这个项目的前端交互抽出来，改成不依赖后端 / 数据库的单文件 HTML」
5. **未与用户确认改造方案前，不构建、不预览、不部署**。

## Windows 运行约定

`scripts/loot_deploy.py` 第一行的 `#!/usr/bin/env python3` 在 Windows 上只当注释，不影响运行；
不要在 PowerShell 里直接执行脚本文件，使用 `py -3 scripts\loot_deploy.py ...`，没有 `py`
命令时使用 `python scripts\loot_deploy.py ...`。

Windows 原生路径：

- 部署令牌配置：`%APPDATA%\loot-flash-apps\config.json`

脚本仍兼容旧位置 `~/.config/loot-flash-apps/config.json`：Windows 原生配置不存在时自动回退
读取。Windows 不执行 POSIX `0600` 权限检查，令牌文件应只保存在当前用户可访问的目录；也可以
改用当前 PowerShell 会话的 `$env:LOOT_DEPLOY_TOKEN`。

## 场景 A：改造已有纯前端项目 → 在副本中 build 单文件 HTML

目标是保留用户现有 React、Vue 或其他纯前端项目的实现，在 `WORKSPACE_DIR` 中运行真实构建，
让 `dist` 等输出目录最终只包含**一个完整 HTML 文件**。不要绕过项目 build，也不要另写一个简化
静态页来冒充 React/Vue 项目的产物。Vite 项目推荐用 `vite-plugin-singlefile` 把 JS/CSS 内联进
`index.html`。

1. 按「原项目只读」创建副本，再在 `WORKSPACE_DIR` 盘点 framework、入口、路由、build script、
   lockfile、静态资源、环境变量、网络请求和浏览器 API。确认这是纯前端项目（见「只支持纯前端」）。
2. 根据副本中的 lockfile 使用原项目的包管理器，在副本中安装依赖并运行已有测试/build。需要下载
   依赖或新增构建插件时先征得用户同意。React/Vue 项目只要存在 build script，就必须实际执行，
   不能仅检查源码后手写 HTML。
3. 如果现有 build 是多文件产物，只修改副本中的构建配置，把它调整为单文件。Vite 项目可在副本中
   安装：

   ```bash
   npm install -D vite-plugin-singlefile
   ```

4. 配置 Vite 把应用 JS/CSS 和本地小资源内联进单个 HTML。以副本里的实际 `vite.config.*` 为准
   合并，不要覆盖既有插件或配置：

   ```ts
   // vite.config.ts
   import { defineConfig } from 'vite'
   import { viteSingleFile } from 'vite-plugin-singlefile'

   export default defineConfig({
     plugins: [/* 既有插件, */ viteSingleFile()],
     build: {
       // 提高内联阈值，尽量把资源转成 data URI 内联进 HTML
       assetsInlineLimit: 100_000_000,
       cssCodeSplit: false,
       rollupOptions: { output: { inlineDynamicImports: true } },
     },
   })
   ```

5. 在 `WORKSPACE_DIR` 构建并确认单文件产物。使用项目实际的包管理器和 build script；以下仅为
   npm 示例：

   ```bash
   npm run build
   # dist 下应只有一个 HTML；确认没有单独的 .js/.css/图片被 HTML 以相对路径引用
   ```

6. 完成「发布前强制质检」，再进入「配置认证信息」和「预览与部署」。预览与发布时把副本产出的
   单文件 HTML 作为 `--html-file` 传入（通常是 `WORKSPACE_DIR/dist/index.html`），并把原项目
   作为 `--project-dir`。

## 场景 B：新建静态页面 → 单文件 HTML

严格产出**一个**完整的 `.html` 文件：

如果是修改用户已有的静态页面，仍须先按「原项目只读」创建副本，所有编辑都在 `WORKSPACE_DIR`
进行。只有完全从零创建、没有既有代码时，才直接在用户指定的新输出目录工作。

1. 所有 CSS 写进 `<style>`，所有 JS 写进 `<script>`，图片用 data URI 或内联 SVG。
2. 不默认引用不稳定的第三方 CDN。需要浏览器端库、WASM 或模型时优先使用 Kiwoo 托管运行时；
   作品可以在运行时联网加载公开 HTTPS 资源，除非用户明确要求离线可用。
3. 不做任何指向自有后端的请求；不内联任何密钥。
4. 如果用户要求的能力需要额外的浏览器端库、WASM 或模型文件，先查看 Kiwoo 托管资源，再考虑
   内联并核对最终大小；没有可行方案时按「保留用户要求的能力」暂停并让用户选择。
5. 用浏览器直接打开该 `.html` 自测主要功能，再进入「发布前强制质检」。

## 发布前强制质检

每次预览前，必须由 Agent 自行完成本节全部检查。原因明确、影响范围小且不改变用户需求或产品
行为的简单问题，可直接修复并重新检查，在结果中说明；涉及功能取舍、产品行为变化、数据风险、
新增依赖或扩大范围时，先向用户说明并取得确认。任何检查未执行、无法执行或失败时，都必须停止，
不得预览或部署。

1. **用户意图保真**：逐项核对用户明确要求的核心能力在产物中真实可用，没有被替换成备用输入、
   模拟效果、占位按钮或解释功能缺失的提示。任何经用户确认的范围变化已记录。
2. **纯前端确认**：无后端 / SSR / 服务端密钥依赖；网络请求要么没有，要么只指向用户已公开
   可访问的接口。
3. **单 HTML 入口**：最终只交付一个 HTML 文件；没有依赖未交付的相对路径 `.js` / `.css` /
   图片。Kiwoo 托管资源或公开 HTTPS 资源可以在运行时加载。用浏览器打开该 HTML，主要功能正常。
4. **无密钥**：HTML 中不含 API key、令牌、私钥或任何敏感凭据。
5. **大小**：HTML 不宜过大（接口有上限，超限返回 413）。避免把大体积模型或其他二进制以
   base64 内联；优先使用 Kiwoo 托管资源，压缩图片、去除未用代码。
6. **记录结果**：预览前向用户简要列出以上各项结果、发现的问题、已完成的修复和待确认事项。
   全部明确通过后才进入预览。

## 配置认证信息

首次部署前必须确保部署令牌已配置。令牌从 Kiwoo 个人中心「获取安装口令」获取；安装口令里已
包含该令牌。未配置时，主动提供以下两种方式：

1. **由 Agent 配置（推荐）**：用户把令牌发到聊天里。收到后不要在回复中复述或展示令牌，去掉
   可选的 `Bearer ` 前缀，用 `configure` 子命令从 **stdin** 写入（绝不经命令行参数）：

   ```bash
   # 令牌通过 stdin 传入；示例用文件避免落进 shell 历史，用完即删
   printf '%s' "$DEPLOY_TOKEN" | python3 "$SKILL_DIR/scripts/loot_deploy.py" configure
   ```

   或直接用你的文件写入能力创建 `~/.config/loot-flash-apps/config.json`（macOS/Linux 权限设
   `0600`；Windows 写到 `%APPDATA%\loot-flash-apps\config.json`，不运行 `chmod`），内容为
   `{"deploy_token": "<令牌>"}`。完成后只确认「部署 token 已配置」，不要输出文件内容或令牌值。

   Windows PowerShell 也可用会话环境变量后从环境读取，避免落盘明文历史：

   ```powershell
   $env:LOOT_DEPLOY_TOKEN = "<令牌>"
   py -3 (Join-Path $SkillDir "scripts\loot_deploy.py") configure --from-env
   ```

2. **由用户配置**：让用户复制模板、替换占位并设置权限：

   ```bash
   SKILL_DIR=/absolute/path/to/loot-flash-apps
   mkdir -p ~/.config/loot-flash-apps
   cp "$SKILL_DIR/assets/config.example.json" ~/.config/loot-flash-apps/config.json
   chmod 600 ~/.config/loot-flash-apps/config.json
   # 编辑该文件，把 deploy_token 替换成个人中心里的令牌
   ```

   ```powershell
   $SkillDir = "C:\absolute\path\to\loot-flash-apps"
   $ConfigDir = Join-Path $env:APPDATA "loot-flash-apps"
   New-Item -ItemType Directory -Force $ConfigDir | Out-Null
   Copy-Item (Join-Path $SkillDir "assets\config.example.json") `
     (Join-Path $ConfigDir "config.json")
   notepad (Join-Path $ConfigDir "config.json")
   ```

令牌也可由用户设为环境变量 `LOOT_DEPLOY_TOKEN`（优先级高于配置文件）。配置后，macOS/Linux
验证文件存在、权限 `0600`、JSON 有效且令牌不是占位值；Windows 验证文件在当前用户
`%APPDATA%`、JSON 有效且令牌不是占位值，不验证 POSIX 权限位。禁止在验证结果中显示令牌。

允许在聊天中接收部署令牌，但**禁止通过 CLI 参数传递**，禁止写入源码、提交记录或产物，也禁止
打印或复制到诊断日志。禁止保存或重放浏览器中的 Cookie、UA 或 `sec-*` 请求头。

## 预览与部署

相对于本 `SKILL.md` 定位 `scripts/loot_deploy.py`。首次部署或排查接口响应时，先读
`references/deploy-api.md`。需要全部参数时运行 `--help`。

用户可见回复必须跟随用户当前部署请求的主要语言。用户用英文请求 `deploy`、`re-deploy` 或继续
部署流程时，整条用户可见回复必须使用英文，包括进度、标题、链接文字、有效期、确认说明、成功结果
和错误说明；不得因为 Skill 的说明是中文而回复中文。用户用中文请求时使用中文。中英混合且意图不明
时，沿用用户最近一条实质性部署指令的主要语言。作品标题等用户原文不强制翻译；CLI 原始输出只作为
内部证据，向用户说明时按回复语言表达。

用户可见的两个步骤名称和确认语按语言固定为：

| 用户语言 | 预览标题 | 发布标题 | 确认语示例 |
|---|---|---|---|
| 中文 | `🌸  **预览作品**` | `🌸  **发布作品**` | `预览没问题，确认发布` |
| English | `🌸  **Preview Work**` | `🌸  **Publish Work**` | `The preview looks good. Confirm publishing.` |

在进度更新、预览链接交付和发布执行中，都用樱花图标加粗显示对应语言的关键词。不要把发布标题写成
「部署确认」或 `Confirm Deployment` 等容易被理解为公开上线的说法。这两个步骤必须出现在不同的
Agent 回复中，标准流程为：完成发布前强制质检 → 显示对应语言的预览标题并交付链接 → 停下等待用户
验证 → 用户用相同语言明确认可预览并授权发布 → 显示对应语言的发布标题并发布到 Kiwoo 草稿箱。
最后一步只保存草稿，不会公开上线。

`API_BASE` 默认 `https://loot.alrite.fun`，可用 `--api` 或环境变量 `LOOT_API_BASE` 覆盖。

每次读取 `preview` 或 `deploy` 的 JSON 输出时都检查可选字段 `skill_update`。当且仅当
`skill_update.available=true` 时，在本次正常结果后按当前对话语言明确转述其中的更新提示，并告诉
用户可以在对话框输入 `升级一下 Loot Skill`。这只是提示：用户没有表达升级意图时，禁止下载、覆盖
或重装当前 Skill；也不得因为存在更新而中断预览或发布到草稿箱。字段不存在表示当前无需提示。

### 预览作品 / Preview Work

此步骤取得 `work_id` 与 10 分钟预览链接：

```bash
python3 "$SKILL_DIR/scripts/loot_deploy.py" preview \
  --html-file /path/to/original-project/.loot/deploy-workspaces/workspace-xxx/dist/index.html \
  --project-dir /path/to/original-project \
  --title "我的应用"
```

- 首次预览会新建一枚草稿，并把稳定的 `work_id` 写入项目目录下 `.loot/loot-artifact.json`。
- 再次预览会自动复用同一 `work_id`（更新同一草稿）；确需新建时加 `--new`；要指定作品用
  `--work-id`。
- **预览新建的草稿是 `status=0`（不公开、不发布），这是预览托管 10 分钟链接的正常机制，
  不等于落库提交，也不会跳过用户确认**——真正的确认闸门在第二步 `deploy` 之前。因此不要
  把「预览会建草稿」当成「已提交」而拒绝预览：`preview` 就是本流程唯一、且正常可用的预览方式，
  没有别的「不建草稿的预览接口」。

Windows PowerShell：

```powershell
$SkillDir = "C:\absolute\path\to\loot-flash-apps"
py -3 (Join-Path $SkillDir "scripts\loot_deploy.py") preview `
  --html-file C:\path\to\original-project\.loot\deploy-workspaces\workspace-xxx\dist\index.html `
  --project-dir C:\path\to\original-project --title "我的应用"
```

从标准输出取得 `preview_url`。链接放在标题后的正文中，并按用户语言选用下面一个模板。

中文：

```markdown
### 🌸  **预览作品**

[打开「{作品标题}」预览]({preview_url})

预览链接有效期为 10 分钟，请尽快打开验证。

确认预览没有问题后，请回复 “预览没问题，确认发布”。发布仅会保存到 Kiwoo 草稿箱，作品仍是草稿，不会公开上线。
```

English:

```markdown
### 🌸  **Preview Work**

[Open the “{work title}” preview]({preview_url})

This preview link is valid for 10 minutes. Please open it soon to verify the work.

Once you have confirmed that the preview looks good, reply “The preview looks good. Confirm publishing.” Publishing only saves the work to your Kiwoo Drafts; it remains a draft and will not go live publicly.
```

交付预览链接的这条回复到此结束。可以提示用户回复对应语言的确认语，但**不得显示发布标题，也不得
在同一轮执行发布。** 然后结束回复，等待用户输入。

- 用户反馈预览仍有问题：继续在副本中修复并重新生成预览，不得进入发布确认。
- 用户只确认预览没有问题、没有明确授权发布：不得执行 `deploy`；请用户明确回复
  与当前回复语言对应的确认语，并再次说明只会保存到 Kiwoo 草稿箱、不会公开上线。
- 用户用当前对话语言明确表达预览无误并授权发布（包括表中确认语或意思同样明确的表达）：才进入
  下一步并执行 `deploy`。
- 若预览链接已过期，重新执行 `preview`（会复用同一 `work_id` 刷新链接），再次等待用户验证。

### 发布作品 / Publish Work

只有用户在收到预览链接后，用当前对话语言明确表达预览认可和发布授权，才执行本步骤。仅表达
`预览没问题` / `The preview looks good` 不构成发布授权。执行时显示与用户语言对应的发布标题；
不需要再向用户重复询问一次。技术命令仍为 `deploy`，把最终 HTML 保存为草稿：

```bash
python3 "$SKILL_DIR/scripts/loot_deploy.py" deploy \
  --work-id WORK_ID \
  --html-file /path/to/original-project/.loot/deploy-workspaces/workspace-xxx/dist/index.html \
  --project-dir /path/to/original-project
```

- 省略 `--work-id` 时脚本自动读取 `.loot/loot-artifact.json` 中的 `work_id`。
- 省略 `--html-file` 时按已有草稿内容直接落库（不改 HTML）。
- 该命令只发布到 Kiwoo **草稿箱**（`status=0`），不会公开上线。

从输出取得 `workspace_url` 交付用户。中文明确说明「已发布到 Kiwoo 草稿箱，尚未公开上线」；英文
明确说明 `The work has been saved to your Kiwoo Drafts and is not publicly live.`。同时说明可在工作台
继续编辑，由用户自行决定是否公开发布。交付 `workspace_url` 后整个流程结束。

`.loot/loot-artifact.json` 只保存稳定的 `work_id`，可纳入项目自己的 Git 仓库，但不要放进任何
构建产物或分发包；只有用户授权时才执行 `git commit`。

## 常见错误

- 禁止只根据 HTTP 200 判断成功；还要确认响应含必要字段（preview: `work_id`/`preview_url`；
  deploy: `work_id`/`workspace_url`）。
- 禁止直接修改、安装依赖或 build 用户的原项目。已有项目必须先复制到项目自身的
  `.loot/deploy-workspaces/workspace-*`，所有写操作只发生在该副本中。
- 禁止把 React/Vue 项目改写成另一个手工静态页来规避构建；必须在副本中 build 原项目，并把真实
  build 产物收敛成单 HTML。
- 禁止部署非纯前端项目；含后端 / SSR / 服务端密钥时先与用户商量只做前端部分或告知不支持。
- 禁止交付需要一起上传的多文件产物；最终必须只有**一个 HTML 入口文件**。运行时加载的 Kiwoo
  托管资源或公开 HTTPS 资源不算多文件交付。
- 禁止以离线、自包含或大小限制为由，未经确认删除摄像头、手势、语音等用户明确要求的核心能力，
  再用备用交互或页面提示替代。
- 禁止在用户确认发布前就保存到草稿箱。必须先交付预览并等待用户输入；只有用户随后明确回复
  与当前对话语言对应的确认语或意思同样明确的表达，才可执行发布。仅确认预览无误不够。
- 禁止在交付预览链接的同一条回复里显示发布标题或执行发布。预览回复可以且必须提示用户在确认
  无误后回复对应语言的确认语；两个步骤必须分属不同回复。
- 用户可见步骤必须使用表中与用户语言对应的标题；不要把确认动作称为部署确认。预览回复中必须用
  同一种语言说明「发布仅会保存到 Kiwoo 草稿箱，不会公开上线」。
- 禁止对英文部署请求使用中文固定文案，或对中文部署请求使用英文固定文案。
- 禁止把「预览会建 `status=0` 草稿」误当成「已提交」而拒绝预览；也不存在「不建草稿的旧预览接口」，
  `preview` 就是唯一且正常可用的预览方式。
- 判定项目无法整体部署时，禁止静默丢个前端单文件了事；必须先按「只支持纯前端」的模板讲清原因、
  给出可选路径与示例 prompt，并等用户确认改造方案。
- 禁止把部署令牌写进 CLI 参数、源码、提交记录、产物或日志。
- 禁止把 `.loot/loot-artifact.json` 里的 `work_id` 之外的东西（令牌、预览 URL、状态）写进该文件。
- 禁止在预览链接旁省略「10 分钟有效期」提醒。
- 遇到 413（过大）时应精简内联资源后重试，不要拆成多文件。
