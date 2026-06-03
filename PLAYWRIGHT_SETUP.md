# Playwright MCP Setup

This lets Claude Code open a real browser, take screenshots, and review your live site.

---

## Setup (3 steps)

### Step 1 — Add Playwright to your Claude Code settings

Open (or create) the file `~/.claude/settings.json`:
- **Mac/Linux:** `~/.claude/settings.json`
- **Windows:** `%USERPROFILE%\.claude\settings.json`

Add the following `mcpServers` section. **Do not replace your whole file** — add only the `mcpServers` block alongside any content already there.

If `settings.json` doesn't exist yet, create it with this content:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest", "--browser", "chromium"]
    }
  }
}
```

If `settings.json` already exists with other content (permissions, theme, etc.), add only the `mcpServers` key:

```json
{
  "permissions": { "...your existing permissions..." },
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest", "--browser", "chromium"]
    }
  }
}
```

The exact content to copy is also in [`config/playwright-mcp-reference.json`](./config/playwright-mcp-reference.json) in this repo (the `mcpServers` block only — ignore the `_comment` key).

> **Why `settings.json` and not a separate file?**
> Claude Code reads MCP server configuration from `~/.claude/settings.json` under the `mcpServers` key. There is no separate `mcp.json` — copying a standalone file will have no effect.

---

### Step 2 — Install Chromium

Run this once in your terminal:

```
npx playwright install chromium
```

This downloads a Chromium browser (~120 MB) that Playwright controls.
It is separate from your regular Chrome — it won't affect your browser bookmarks or settings.

---

### Step 3 — Restart Claude Code completely

Close Claude Code and reopen it. A new session in the same window is **not enough** — the MCP server only loads on full restart.

**Mac:** Quit Claude Code (Cmd+Q), then reopen it.
**Windows:** Close the window, then reopen from the Start menu.

---

## Verify it works

After restarting, give Claude Code this prompt:

> "Open https://example.com in a browser and describe what you see."

Claude should navigate to the page, take a screenshot, and describe it. If you see an error about Playwright not being found, check the steps below.

---

## Common problems

**Playwright commands not available after restart**
Check that `settings.json` is in the right location and that it contains a valid `mcpServers` key. Common mistake: editing a project-local settings file instead of the global `~/.claude/settings.json`. Also confirm you did a full quit-and-reopen (not just a new session tab).

**"Could not find browser"**
Run `npx playwright install chromium` again. The browser may not have downloaded fully.

**"npx: command not found"**
Node.js is not installed. Download it from [nodejs.org](https://nodejs.org) (choose the LTS version).

---

## What you can do with it

Once set up, you can ask Claude Code things like:

- "Open my CloudFront URL and take a screenshot — does the layout look right?"
- "Check if the contact form on [URL] is working"
- "The mobile layout looks broken on my phone — can you open it in a mobile viewport and fix it?"
- "Compare this page to my design reference image and tell me what's different"
