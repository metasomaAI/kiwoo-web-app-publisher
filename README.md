# Kiwoo Web App Publisher

Cross-platform distribution of the production Kiwoo publishing skill, packaged
for OpenAI Codex/ChatGPT, Claude Code/Claude Directory, and WorkBuddy.

- Version: `1.1.1`
- Publisher: Kiwoo Lab
- Category: Developer Tools
- Repository: https://github.com/metasomaAI/kiwoo-web-app-publisher
- Website: https://kiwoo.ai
- Support: support@kiwoo.ai

## What it does

Preview and publish pure-frontend HTML apps to Kiwoo drafts, with an explicit preview-then-confirm workflow.

The agent first builds a single-file, pure-frontend HTML entry, runs a
pre-publish quality gate, and creates a 10-minute Kiwoo preview link. It must
stop there and wait for the user's explicit confirmation in the same language.

**Preview first, then confirm, draft-only.** After explicit confirmation the
agent saves the work to Kiwoo Drafts with `status=0`. This is not a public
release: the work is never made publicly live by this plugin. The user decides
later in the Kiwoo workspace whether to publish publicly.

## Install

### OpenAI Codex / ChatGPT

Use the repository marketplace catalog at `.agents/plugins/marketplace.json`, or
install the plugin package directory directly. The manifest is
`.codex-plugin/plugin.json`; the included square package icon is
`icon-192.png`, referenced as `interface.logo` and `interface.composerIcon`.

### Claude Code / Claude Directory

Add this repository as a marketplace, then install
`kiwoo-web-app-publisher@kiwoo`. The manifest is
`.claude-plugin/plugin.json`, and the skill ships at
`skills/kiwoo-web-app-publisher/SKILL.md`.

### WorkBuddy

Upload the generated `kiwoo-web-app-publisher-workbuddy.zip` through **Skills -> Add Skill ->
Upload Skill**. Its single top-level directory contains `SKILL.md` at the root
plus the copied `scripts/`, `references/`, `assets/`, and
`skill-manifest.json` resources.

## Setup

1. Create a Kiwoo deploy token at https://kiwoo.ai/settings/tokens.
2. Give the token to the agent through chat, the `LOOT_DEPLOY_TOKEN` environment
   variable, or the platform config file. The bundled `configure` command reads
   the token from **stdin only**; it is never accepted as a CLI argument.
3. Ask the agent to preview a pure-frontend project or static HTML page, verify
   the preview, then explicitly confirm publishing.

Never commit a deploy token. Never pass a token as a command-line argument.

## Supported scope

- Pure-frontend projects that can be built into **one complete HTML file**.
- Static pages whose CSS, JavaScript, and small assets can be inlined.
- Browser-side dependencies served from Kiwoo-managed runtimes or from public
  HTTPS URLs.

Not supported: backends, SSR, server routes, databases, server-side secrets,
multi-file delivery, or inlining API keys into the page. If a requested
capability needs a server or a secret, the agent must stop and explain the
options instead of silently removing that capability.

## Privacy and security

- **Network:** the bundled deploy script talks only to the Kiwoo deploy API
  (`https://loot.alrite.fun` by default, overridable with `--api` or
  `LOOT_API_BASE`). The plugin itself contains no telemetry, analytics, or
  background network calls.
- **Credentials:** a deploy token authenticates only the deploy API. The script
  sends it in the `Authorization: Bearer` header, stores it outside the project
  (XDG config or `%APPDATA%`) with restricted permissions where supported, and
  never logs it. Browser cookies, user-agent strings, and `sec-*` headers are
  never captured or replayed.
- **Files:** the agent reads the user's project and writes a working copy under
  the project's own `.loot/deploy-workspaces/` directory. Source projects are
  treated as read-only. Generated `.loot/loot-artifact.json` contains only the
  stable `work_id` and must not be committed to a build artifact.
- **User data:** the plugin does not collect, sell, or share personal data. The
  Kiwoo service processes the HTML, title, and account identity needed to create
  drafts and previews, as described in the privacy policy.
- **Third-party content:** a published work may load public HTTPS resources; the
  browser can then send requests to those third-party hosts. The agent should
  disclose such dependencies and must never add a secret to make them work.

Canonical links: [website](https://kiwoo.ai) |
[token setup](https://kiwoo.ai/settings/tokens) |
[privacy](https://kiwoo.ai/privacy) | [terms](https://kiwoo.ai/terms) |
[support](mailto:support@kiwoo.ai)
