# Playwright MCP Setup

This lets Claude Code open a real browser, take screenshots, and review your live site.

---

## Setup (3 steps)

### Step 1 — Copy the config file

**Mac:**
```
cp config/playwright-mcp.json ~/.claude/mcp.json
```

**Windows** (run in PowerShell):
```
Copy-Item config\playwright-mcp.json $env:USERPROFILE\.claude\mcp.json
```

If the `.claude` folder doesn't exist yet, create it first:
- Mac: `mkdir -p ~/.claude`
- Windows: `New-Item -ItemType Directory -Path $env:USERPROFILE\.claude`

> **Where Claude Code looks for MCP config:**
> - Mac/Linux: `~/.claude/mcp.json`
> - Windows: `%USERPROFILE%\.claude\mcp.json`
>
> You can also place `mcp.json` inside your project folder to keep it project-specific.

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

Claude should navigate to the page, take a screenshot, and describe it. If you see an error about Playwright not being found, go back to Step 2.

---

## Common problems

**"Could not find browser"**
Run `npx playwright install chromium` again. The browser may not have downloaded fully.

**"MCP server not found" or Playwright commands not available**
You need a full restart of Claude Code (not just a new session). Also check that `mcp.json` is in the right location — the path must be exact.

**"npx: command not found"**
Node.js is not installed. Download it from [nodejs.org](https://nodejs.org) (choose the LTS version).

---

## What you can do with it

Once set up, you can ask Claude Code things like:

- "Open my CloudFront URL and take a screenshot — does the layout look right?"
- "Check if the contact form on [URL] is working"
- "The mobile layout looks broken on my phone — can you open it in a mobile viewport and fix it?"
- "Compare this page to my design reference image and tell me what's different"
