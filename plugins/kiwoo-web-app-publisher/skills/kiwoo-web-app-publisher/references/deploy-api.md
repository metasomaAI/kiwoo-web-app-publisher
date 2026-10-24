# Kiwoo 一键部署接口

只在首次部署、排查接口响应或需要核对字段时读取本文档。所有接口都以部署令牌
（Deploy Token）鉴权，与网站登录态完全无关。

## 认证

在 Kiwoo 个人中心「获取安装口令」处生成部署 token。令牌形如 `loot_deploy_xxx`，
每个用户唯一，可随时在个人中心重新查看或轮换（轮换后旧令牌立即失效）。

除正常 HTTP 协议头外，只发送以下请求头：

```text
Accept: application/json
Content-Type: application/json; charset=utf-8
Authorization: Bearer <deploy-token>
User-Agent: loot-flash-apps-cli/1.1.1
X-Loot-Skill-Version: 1.1.1
```

禁止保存或重放任何从浏览器复制的 Cookie、User-Agent、`sec-ch-*` 或 `sec-fetch-*`
请求头。部署令牌只经 `Authorization` 头发送，禁止写入 URL、命令行参数或日志。

## 升级包下载

升级提示中的版本固定地址形如
`/api/deploy/skills/1.1.1/loot-flash-apps.zip`。如果该版本已不可用，服务端返回
`404 + Cache-Control: no-store`，并在 `X-Loot-Skill-Version` 响应头以及 JSON
`detail.latest_version`、`detail.update_url` 中给出当前版本和规范下载路径。安装器应将其
作为可见诊断信息，不能静默改装另一个版本。

## 预览

用户可见回复跟随当前部署请求的主要语言。中文标题使用 `🌸  **预览作品**`，英文标题使用
`🌸  **Preview Work**`；英文请求下，链接文字、有效期、确认说明和草稿说明也全部使用英文。

```text
POST {API_BASE}/api/deploy/preview
Content-Type: application/json
```

`API_BASE` 默认 `https://loot.alrite.fun`，可用 `--api` 或环境变量 `LOOT_API_BASE` 覆盖。

请求体字段：

| 字段 | 是否必填 | 含义 |
|---|---:|---|
| `html` | 是 | 完整 HTML 文本；应用代码应内联，运行时可以引用绝对 HTTPS 资源 |
| `title` | 否 | 作品标题 |
| `work_id` | 否 | 复用已有草稿；省略则新建一枚草稿作品 |

成功响应示例：

```json
{
  "work_id": "w_abcdef123456",
  "preview_url": "https://kiwoo.ai/preview/w_abcdef123456?preview_token=eyJ...",
  "expires_at": "2026-08-25T09:10:00Z",
  "expires_in": 600
}
```

`preview_url` 自签发起有效期为 **10 分钟**（`expires_in` 秒）。向用户交付预览链接时，
必须紧邻链接明确说明该有效期，并提醒尽快在浏览器打开验证。`work_id` 是稳定的作品身份，
命令行工具会写入 `.loot/loot-artifact.json` 以便后续复用同一草稿。

preview 和 commit 的成功响应都可能额外包含非阻断更新提示：

```json
{
  "skill_update": {
    "available": true,
    "current_version": "1.0",
    "latest_version": "1.1.1",
    "message": "Loot Skill 有新版本 1.1.1，可获得最新能力。请在对话框输入：升级一下 Loot Skill",
    "upgrade_command": "升级一下 Loot Skill",
    "update_url": "https://loot.alrite.fun/api/deploy/skills/1.1.1/loot-flash-apps.zip"
  }
}
```

只有实际调用接口的旧版官方 Skill 会收到该字段。Agent 必须在正常部署结果后按当前对话语言转述
升级提示；用户没有表达升级意图时不得下载或覆盖安装，存在提示也不得中断当前 preview/commit。
字段不存在时无需向用户提及版本。

交付预览链接时按用户语言选用以下一个模板，并在标题后的正文中提供实际链接。

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

回复到此结束，不得在同一条回复中显示发布标题或调用发布接口。用户报告问题时修复后重新预览。
只有用户用当前对话语言明确表达预览认可和发布授权，Agent 才能执行发布；仅表达
`预览没问题` / `The preview looks good` 不构成发布授权。

## 发布到 Kiwoo 草稿箱

中文用户可见标题使用 `🌸  **发布作品**`，英文使用 `🌸  **Publish Work**`。只有用户在收到
预览链接后，用当前对话语言明确表达预览认可和发布授权，才允许调用下面的接口；仅确认预览无误
不构成发布授权。执行发布时可在单独的 Agent 回复中显示对应语言的标题，不需要再重复询问一次。
目标始终是 Kiwoo 草稿箱，作品不会公开上线；不要把确认动作称为部署确认或 `Confirm Deployment`。
`commit` / `deploy` 只是 API 和命令行里的技术名称。

```text
POST {API_BASE}/api/deploy/commit
Content-Type: application/json
```

请求体字段：

| 字段 | 是否必填 | 含义 |
|---|---:|---|
| `work_id` | 是 | 目标草稿作品 ID（来自 preview 或 `.loot/loot-artifact.json`） |
| `html` | 否 | 最终 HTML；省略时按已有草稿内容直接落库 |
| `title` | 否 | 作品标题 |

成功响应示例：

```json
{
  "work_id": "w_abcdef123456",
  "workspace_url": "https://kiwoo.ai/workspace?draft=w_abcdef123456"
}
```

commit 只把作品**发布到 Kiwoo 草稿箱**（`status=0`），不会公开上线。是否公开由用户随后在站内
「我的创作」/工作台自行完成。向用户交付 `workspace_url` 时说明「已发布到 Kiwoo 草稿箱，尚未
公开上线」；英文说明 `The work has been saved to your Kiwoo Drafts and is not publicly live.`。
同时说明可在工作台继续编辑或公开发布。

## 大小限制

HTML 有大小上限。超限时接口返回 HTTP 413，响应体形如 `{"detail": "..."}`。命令行工具会
原样透传该原因；此时应精简内联内容（压缩图片、去除未用代码、避免把大体积二进制以 base64
内联），或改用 `runtime-assets.md` 中的 Kiwoo 托管资源后重试。不要因此删除用户要求的功能，也不要
改成交付一组需要一起上传的本地文件。

## 失败判定

出现以下任一情况都判定为失败：

- HTTP 状态码不在 200–299 范围内。
- 响应正文不是 JSON 对象。
- 缺少必要结果字段（preview 缺 `work_id`/`preview_url`；commit 缺 `work_id`/`workspace_url`）。

命令行工具在脱敏后的诊断信息中会保留接口返回的 `detail`，但**绝不输出部署令牌**。
非 2xx 响应不会自动重试；网络失败且结果不明确时，先确认草稿是否已建立，再决定是否重试。
