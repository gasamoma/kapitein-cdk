# GSDevTools

## ⚠️ Development-only — remove before deploy
GSDevTools renders a visible playback UI (scrubber, play/pause, timeScale controls, keyboard shortcuts) directly in the browser. **It must never ship to production.** Before pushing to `main` / deploying, remove its `<script>` tag, its `gsap.registerPlugin(GSDevTools)` entry, and every `GSDevTools.create(...)` call. Treat it exactly like `MotionPathHelper` — a tool you reach for while building, then strip out.

## What it's for
Reach for GSDevTools when you're building or debugging a complex animation sequence (a multi-step hero timeline, a scroll-driven choreography, anything with several moving parts) and need to **scrub through it, slow it down, jump to specific moments, or isolate a section** to see exactly what's happening at a given instant — far faster than repeatedly refreshing the page and waiting for the animation to replay.

## Setup
```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/GSDevTools.min.js"></script>
<script>
  gsap.registerPlugin(GSDevTools);

  const tl = gsap.timeline({ id: 'heroIntro' });
  tl.from('.hero-title', { opacity: 0, y: 60, duration: 0.8 })
    .from('.hero-cta', { opacity: 0, y: 30, duration: 0.6 }, '-=0.3');

  // DEV ONLY — remove this line before deploying:
  GSDevTools.create({ animation: tl });
</script>
```
No other plugin dependencies. It works with any GSAP Tween or Timeline — it just needs a reference (or it'll fall back to controlling the global timeline, see gotchas).

## Key concepts
- **Link it to a specific animation whenever possible**: `GSDevTools.create({ animation: tl })`. Without an `animation`, it defaults to controlling the *global timeline* (every animation on the page at once), which is heavier and more confusing to read.
- **Give your tweens and timelines `id`s** (`gsap.timeline({ id: 'heroIntro' })`, `tl.to(el, { ..., id: 'titleReveal' })`) — each id shows up in the GSDevTools animation-picker menu, letting you jump straight to the scene you care about instead of hunting through an unlabeled list.
- **In/out points and other settings persist across page refreshes** (scoped by id + session + domain). Drag the in/out markers to isolate a section, tweak your code, refresh, and it stays cropped to that section — a fast iteration loop. Set `persist: false` to disable this if it ever causes "contamination" between instances (or give each instance a unique `id` to segregate the stored state).
- **Keyboard shortcuts make scrubbing fast** once the UI has focus: `SPACE` play/pause, `↑`/`↓` change timeScale, `←` rewind, `→` jump to end, `L` toggle loop, `I`/`O` set in/out points at the playhead, `H` hide/show the UI overlay (handy when it's covering the thing you're inspecting — shortcuts still work while hidden).
- **`.create()` returns an instance you can later `.kill()`** — give it an `id` (`GSDevTools.create({ id: 'main' })`) so you can clean it up with `GSDevTools.getById('main').kill()`, e.g. when hot-reloading during development.

## Common gotchas
- **It does NOT work with ScrollTrigger-driven animations.** The docs explicitly call this out: having both the page scrollbar and the GSDevTools scrubber try to drive the same animation is "logically impossible," and the community has reported it can interfere with ScrollTrigger firing at all when both are active on a page. If your landing page is built around scroll-triggered reveals (which most are), GSDevTools is the wrong tool — see the lightweight alternative below.
- **An infinitely-repeating animation produces a "1000 second" global timeline.** This is GSDevTools capping the duration so the scrubber stays usable (scrubbing to `Infinity` would be meaningless) — it's expected behavior, not a bug, but it's a confusing first encounter if you weren't expecting it.
- **Only one instance can listen for keyboard shortcuts at a time** (`keyboard: true`, the default). Multiple `GSDevTools.create()` calls on a page will conflict over keyboard control — pick one to own the shortcuts, or set `keyboard: false` on the others.
- **It only works with GSAP animations** — it depends on internals unique to GSAP's architecture and won't recognize or control animations from other libraries (CSS animations, other JS animation tools, etc.).
- **It's easy to forget to remove before deploy** because it's just a few lines and doesn't break anything functionally — but it does add an unwanted floating UI element to your shipped page, plus an extra script download. Grep for `GSDevTools` as a final pre-deploy check.

## The lightweight, no-dependency alternative: `gsap.globalTimeline`
For most "I just need to see what the animation looks like halfway through" needs — especially with ScrollTrigger involved — skip the extra script entirely and drive GSAP's `globalTimeline` (every Tween/Timeline's ultimate parent) directly from the browser console:

```js
// Pause everything on the page right where it is:
gsap.globalTimeline.pause();

// Jump to a specific point (0 = start, 1 = end) to inspect that exact frame:
gsap.globalTimeline.progress(0.5);

// Step through frame-by-frame to debug a tricky transition:
gsap.globalTimeline.progress(0.42);
gsap.globalTimeline.progress(0.43);
gsap.globalTimeline.progress(0.44);

// Resume normal playback when done:
gsap.globalTimeline.play();
```
This uses only the standard Animation-class methods (`pause()`, `play()`, `progress()`) that every Tween and Timeline already exposes — nothing to install, nothing to register, nothing to remember to remove before shipping. It's less convenient than a visual scrubber UI, but it's "free," works fine alongside ScrollTrigger, and is often all you need to confirm a mid-animation state looks right.

## Recipes
GSDevTools doesn't have "landing page" recipes in the usual sense — it's a debugging tool, not a visitor-facing effect. The setup snippet above (link to a named timeline, give children `id`s) is the complete recommended pattern. Use it locally while iterating on a hero or scroll sequence, confirm the timing feels right, then delete it.

## When to skip it
- **Skip it whenever ScrollTrigger drives the animation** (most landing-page scroll reveals) — use `gsap.globalTimeline.pause()` + `.progress(n)` instead.
- **Skip it for simple, short tweens** where just watching the page reload a couple of times is faster than wiring up the tooling.
- **Always skip shipping it** — there is no scenario where GSDevTools belongs in a production build.
