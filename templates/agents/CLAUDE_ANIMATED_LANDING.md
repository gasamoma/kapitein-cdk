# Animated Landing Page Agent — kapitein-cdk

You are building an animated landing page using the kapitein-cdk serverless stack.
Use GSAP for all animations. Make the page feel modern, smooth, and polished.

## Your job

Build a single-page landing site in `src/frontend/`. No frameworks, no build step — just HTML, CSS, and JavaScript loaded from CDN. When finished, remind the user to push to the `main` branch to deploy.

---

## BEFORE WRITING ANY CODE — READ THE PAGE FIRST

If `src/frontend/index.html` already exists, **read it completely before making any changes.** Extract and reuse:
- Which GSAP plugins are already in `<script>` tags — do NOT add duplicates
- Which plugins are already in `gsap.registerPlugin(...)` — extend that call, don't replace it
- The existing CSS custom properties (`--accent`, `--surface`, etc.) — use them, don't invent new ones
- The existing class naming conventions — extend them consistently
- Any utility functions or animation patterns already defined in `<script>` — reuse them

**Never reinvent something that's already available on the page.** If SplitText is already loaded, use it. If a `startHero()` function exists, call it. If `--accent` is the brand color, use it.

This applies to edits AND new features. Always audit the existing page before writing a single line.

Ask the user:
1. What is this landing page for? (product, service, event, personal brand?)
2. What is the single most important action visitors should take? (sign up, book, buy, contact?)
3. How should it feel — bold and dramatic, clean and minimal, warm and personal, or something else?
4. What sections does it need? (suggest: Hero, Features/Benefits, Social proof, CTA, Footer)

After getting answers, build the full page without further questions.

---

## Stack

### File locations
- `src/frontend/index.html` — the entire page (one file is fine for a landing page)
- `src/frontend/css/style.css` — styles (or inline in `<style>`)
- `src/frontend/js/main.js` — GSAP animations and interactivity (or inline in `<script>`)
- Images: `src/frontend/images/`

---

## GSAP Plugin Reference

**ALWAYS use `gsap@3.15` — do not pick a different version number.**

All plugins below are available at `https://cdn.jsdelivr.net/npm/gsap@3.15/dist/<Plugin>.min.js` and are free to use.

Include only the plugins you actually need for the page. Register all of them together before any animation code runs.

### Plugin Dictionary

| Plugin file | What it does | Use it when |
|---|---|---|
| `gsap.min.js` | Core engine — tweens, timelines, all property animation | **Always. This is required.** |
| `ScrollTrigger.min.js` | Triggers animations on scroll position | Any scroll-based reveal, parallax, or pin |
| `SplitText.min.js` | Splits text into animatable words, chars, or lines | Hero headlines, word-by-word reveals, line wipes |
| `ScrollSmoother.min.js` | Smooth momentum scroll + built-in parallax (requires ScrollTrigger) | Premium feel — silky scroll with depth |
| `ScrollToPlugin.min.js` | Animates the viewport scrolling to a target | Smooth nav anchor links, "back to top" |
| `Observer.min.js` | Detects scroll/touch/pointer direction and velocity | Custom scroll behaviors, horizontal scroll sections |
| `Flip.min.js` | Smoothly animates elements between different DOM states/positions | Filter grids, tab switches, layout morphing |
| `Draggable.min.js` | Makes elements draggable with bounds and callbacks | Sliders, carousels, interactive drag UIs |
| `InertiaPlugin.min.js` | Momentum/throw physics after releasing a Draggable | Carousel that coasts after a flick |
| `ScrambleTextPlugin.min.js` | Text scrambles with random chars before settling on final text | Hacker/tech reveals, terminal aesthetic, stats counters |
| `TextPlugin.min.js` | Animates text content character by character | Typewriter effect |
| `DrawSVGPlugin.min.js` | Animates SVG stroke-dashoffset to "draw" paths | Drawing lines, signature animations, icon outlines appearing |
| `MorphSVGPlugin.min.js` | Smoothly morphs one SVG path shape into another | Logo transitions, icon state changes |
| `MotionPathPlugin.min.js` | Animates an element along an SVG `<path>` | Flying objects, orbits, curved entrances |
| `MotionPathHelper.min.js` | Dev overlay UI to edit motion paths visually | **Development only — remove before deploy** |
| `Physics2DPlugin.min.js` | Gravity, friction, acceleration on 2D position | Confetti, particle bursts, falling elements |
| `PhysicsPropsPlugin.min.js` | Physics forces on arbitrary CSS/SVG properties (not just x/y) | Custom physics simulations |
| `EasePack.min.js` | Adds `RoughEase`, `ExpoScaleEase`, `SlowMo` easing functions | Organic/rough movement, bouncy overshoots |
| `CustomEase.min.js` | Define any easing curve as an SVG cubic path string | Precise branded timing curves |
| `CustomBounce.min.js` | Custom bounce easing (requires CustomEase) | Cartoonish bouncy drops |
| `CustomWiggle.min.js` | Custom oscillation/wiggle easing (requires CustomEase) | Attention-grabbing jiggle effects |
| `GSDevTools.min.js` | Visual timeline debugger UI in the browser | **Development only — remove before deploy** |
| `EaselPlugin.min.js` | Integrates GSAP with CreateJS/EaselJS canvas API | Canvas/game projects using EaselJS only |
| `PixiPlugin.min.js` | Integrates GSAP with Pixi.js WebGL renderer | WebGL projects using Pixi.js only |

### How to include and register plugins

```html
<!-- Always include core first -->
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/gsap.min.js"></script>

<!-- Then add only the plugins you need, e.g.: -->
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/ScrollTrigger.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/SplitText.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/ScrambleTextPlugin.min.js"></script>

<!-- Register everything before writing any animation code -->
<script>
  gsap.registerPlugin(ScrollTrigger, SplitText, ScrambleTextPlugin);
  // All animation code goes here (DOM is ready since this script is at bottom of <body>)
</script>
```

**Important:** Always `registerPlugin()` before calling `new SplitText()`, `ScrollTrigger.create()`, etc. — even though GSAP auto-registers when loaded via `<script>`, explicit registration prevents tree-shaking issues and makes the code intention clear.

**Before using any plugin for the first time on this page**, read its deep-dive guide at `templates/agents/gsap/<PluginName>.md` (e.g. `templates/agents/gsap/Flip.md`, `templates/agents/gsap/ScrollTrigger.md`). The dictionary above tells you *when* to reach for a plugin — those guides tell you the gotchas and idioms that separate "technically works" from "looks professional," so you get it right the first time instead of debugging it live.

---

## Animation patterns

**Hero entrance — SplitText word reveal with stagger:**
```js
// SplitText.create() is the current API (replaced `new SplitText()` in v3.13 — see templates/agents/gsap/SplitText.md)
const heroTitle = SplitText.create('.hero-title', { type: 'words' });
gsap.set(heroTitle.words, { opacity: 0, y: 60, rotateX: -60, transformPerspective: 600, transformOrigin: 'center bottom' });
// Then on DOMContentLoaded or immediately (script is at bottom of body):
gsap.to(heroTitle.words, {
  opacity: 1, y: 0, rotateX: 0,
  stagger: { amount: 0.5, from: 'start' },
  duration: 0.7, ease: 'power4.out'
});
gsap.to('.hero-subtitle', { opacity: 1, y: 0, duration: 0.7, delay: 0.4 });
gsap.to('.hero-cta',      { opacity: 1, y: 0, duration: 0.6, delay: 0.7 });
```

**Section title line reveal (SplitText lines):**
```js
document.querySelectorAll('.section-title').forEach(el => {
  SplitText.create(el, {
    type: 'lines',
    onSplit(self) {
      return gsap.from(self.lines, {
        opacity: 0, y: 50, stagger: 0.1, duration: 0.8, ease: 'power3.out',
        scrollTrigger: { trigger: el, start: 'top 88%' }
      });
    }
  });
});
```

**Scroll reveals — staggered cards:**
```js
gsap.from('.card', {
  opacity: 0, y: 60, scale: 0.95, stagger: 0.1, duration: 0.8, ease: 'power3.out',
  scrollTrigger: { trigger: '.cards-wrapper', start: 'top 85%' }
});
```

**Parallax orbs / background layers:**
```js
gsap.to('.orb', {
  y: -120, ease: 'none',
  scrollTrigger: { trigger: '#hero', start: 'top top', end: 'bottom top', scrub: 1.5 }
});
```

**ScrambleText stat counter reveal:**
```js
gsap.to('.stat-number', {
  duration: 1.5,
  scrambleText: { text: '{original}', chars: '0123456789', revealDelay: 0.3 },
  scrollTrigger: { trigger: '.stats', start: 'top 80%' }
});
```

**Sticky nav on scroll:**
```js
ScrollTrigger.create({
  start: 'top -60',
  onUpdate: self => {
    document.querySelector('nav').classList.toggle('scrolled', self.progress > 0);
  }
});
```

**Morphing an element from one layout/state into another (Flip):**
The clean way to fly something from a splash screen into its place in the nav, or grow a card into an expanded view — snapshot the "before" layout, mutate the DOM into the "after" state, then let Flip animate the difference for you. No manual `getBoundingClientRect()` math, no clones to fade in and out.
```js
const state = Flip.getState(el);          // 1. snapshot current position/size/etc.
el.classList.add('final-position');       // 2. make the DOM change INSTANTLY
otherEl.remove();                         //    (move in DOM, swap classes — whatever the "after" state needs)
Flip.from(state, {                        // 3. Flip plays the difference as an animation
  duration: 0.7, ease: 'power3.inOut',
  onComplete: () => { /* chain the next step here */ }
});
```

---

## API (only if the page has a form)

Load the API URL from the injected config:
```js
fetch('/config.json')
  .then(r => r.json())
  .then(config => { window.API_BASE_URL = config.apiUrl; });
```

POST to `window.API_BASE_URL` with `{ name, email, message, source }`.

### CORS
Lambda Function URL CORS is configured in the CDK stack. Do not add CORS headers manually in the handler.

### Deploying and verifying — every time, before you say "done"

1. **Push to `main`.** GitHub Actions builds and deploys automatically — no local tools needed.

2. **Don't poll for deploy status — and don't assume `gh` (GitHub CLI) is installed.** This project's whole premise is "no local tools required," so never rely on `gh run watch`, `gh run list`, or any other CLI the user would have to install themselves. Repeatedly checking the Actions tab yourself is just as bad — it burns calls and makes you look stuck. Instead:
   - Tell the user ONCE, up front: a deploy takes roughly 4 minutes once the pipeline is warm, and up to ~10 minutes on a first run (Docker bundling, CDK bootstrap, CloudFront distribution creation).
   - Then simply **let the conversation continue naturally** — wrap up other things, answer questions, or ask the user to give you the word when they think it's ready. The back-and-forth itself provides the wait; you don't need to manufacture one.
   - When you do check, **check the live CloudFront URL for the actual change** (see step 3) rather than checking whether a pipeline *says* it succeeded — that's the outcome that actually matters to the user, and it sidesteps GitHub Actions entirely.
   - If the change isn't visible yet, say so plainly ("still deploying — give it a few more minutes and I'll look again") and wait for the next natural pause before re-checking. Never loop silently.

3. **Test the LIVE CloudFront URL — never test a local copy.** This page calls a live API (`/config.json`, the lead-capture endpoint); a `file://` origin can't reach either, so a "local" test would pass or fail for the wrong reasons. Get the CloudFront URL from the stack outputs / `cdk deploy` output / CloudFormation console, then drive Playwright at that URL. (CloudFront caches aggressively — if you push a change and the live page still looks like the old version, that's likely cache, not a failed deploy. Try a hard reload or a cache-busting query string like `?v=2` before concluding something's wrong.)

### What to verify — review it like a picky designer, not a smoke-tester

Don't just confirm the page loads. Walk through this checklist on the live URL:

**Console & network**
- Zero console errors or warnings (`browser_console_messages`)
- `/config.json` loads and `window.API_BASE_URL` gets set
- No 404s for scripts, fonts, or images (`browser_network_requests`)

**Visual QA — the picky pass**
- No overlapping text or elements
- No text or images clipped/cut off by their containers
- Things that should be centered actually look centered (icons/padding can throw off optical balance)
- Consistent spacing and rhythm between sections — nothing cramped or oddly loose
- Real contrast between text and background — on a dark theme, watch for "dark grey on black" text
- Type realistic content into any form fields (a real name, a longer email, a multi-sentence message) and confirm nothing breaks the layout — don't only check the empty state

**Responsiveness**
- Re-run the visual QA pass at 375px (mobile), ~768px (tablet), and ~1440px (desktop) — layout bugs hide at breakpoints, not in the middle of them
- Confirm the nav/menu works at mobile width

**Forms (if the page has one)**
- Fill every field with realistic values and submit
- Confirm the user sees an actual success state — not just a 200 in the network log
- Submit with a required field missing and confirm a sensible error shows
- Inspect the request body and response in `browser_network_requests`

**Animations — what screenshots can and can't tell you**
A still frame can't judge whether motion *feels* right — timing, easing, and stagger read completely differently in motion than frozen. Don't try to fully grade animation quality from screenshots. Instead:
- Confirm each animation actually fires (a couple of screenshots a beat apart should show visible change)
- Hunt specifically for elements stuck invisible — a `gsap.set(el, {opacity: 0})` whose matching `.to()` never ran is the most common real bug, and the easiest to miss in a single screenshot
- Beyond that, get the configuration right up front and trust GSAP to handle the rest — see the per-plugin guides in `templates/agents/gsap/` for the gotchas that prevent these bugs before you ever open a browser

### Where test artifacts go
Save every screenshot, trace, or log to `.playwright-mcp/` — it's gitignored, so nothing pollutes the repo or `git status`. Use descriptive names: `.playwright-mcp/hero-mobile-375.png`, `.playwright-mcp/form-success-state.png`, not `screenshot1.png`. Never write artifacts to the repo root.

---

## Design principles

- **Performance**: animate only `transform` and `opacity` — never `width`, `height`, `top`, `left`
- **Respect motion**: wrap all animations in `if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches)`
- **Initial states via GSAP, ALL of them, up front**: use `gsap.set()` to hide elements before animating them — never `opacity: 0` in CSS, because if JS fails the content stays visible. Set every element that *any* animation on the page will eventually reveal in ONE block at the very top of your script, before any sequencing runs — not inside the function that plays its entrance. (Real bug from this project: hero elements were hidden only inside the function that animated them in, which ran *after* a multi-second intro sequence — so they sat fully visible behind the intro the whole time it played.)
- **One strong CTA**: every section flows toward the single action the user identified
- **Mobile-first CSS**: design for 375px, then `min-width` media queries up
- **Smooth scroll**: `html { scroll-behavior: smooth; }` + anchor links for all sections
