# CustomEase

## What it's for
Reach for CustomEase when none of GSAP's built-in eases (`power2.out`, `back.out`, `expo.inOut`, etc.) produce the exact timing curve your brand or design calls for. It lets you define **any** easing curve — by drawing it, pasting an SVG path, or pasting a `cubic-bezier()` string — and then reference it by name everywhere, like a first-class ease. It's the foundation plugin that `CustomBounce` and `CustomWiggle` are built on top of.

## Setup
```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/CustomEase.min.js"></script>
<script>
  gsap.registerPlugin(CustomEase);
</script>
```
No other plugin dependencies — CustomEase is the base. (`CustomBounce` and `CustomWiggle` both *extend* CustomEase and require it to be loaded and registered first — see their respective docs.)

## Key concepts
- **Two-step workflow: create once, reference by string forever after.** `CustomEase.create("hop", "M0,0 C0,0 ...")` builds and caches the curve under the ID `"hop"`; from then on you just write `ease: "hop"` in any tween, exactly like a built-in ease name.
- **Create eases at load time, not inside animation code.** There's real overhead in calculating and optimizing all the curve points — that cost is paid once, at `create()` time, so the runtime tween stays blazing fast. Defining eases inside a function that runs on every interaction (hover, click, scroll callback) re-does that work needlessly — and worse, repeatedly overwrites the same ID.
- **Three input formats, all accepted by `create()`:** (1) a normalized SVG path string (`"M0,0 C0.1,0.2 ..."`, values 0–1), (2) raw SVG path data copied from a tool like Illustrator (any path using `M`, `C`, `S`, `L`, `Z` — GSAP normalizes it internally), or (3) a `cubic-bezier()`-style 4-number string like `".17,.67,.83,.67"` (the same format sites like cubic-bezier.com produce).
- **The Ease Visualizer on the GSAP docs site** lets you draw a curve interactively and copy out the path string — by far the easiest way to author a CustomEase without hand-writing SVG path data.
- **`getSVGData()` renders any ease — custom or built-in — as an SVG path** for visualization: `CustomEase.getSVGData("hop", { width: 500, height: 400, path: "#easeViz" })`. Handy for debugging what a curve actually looks like in-browser, or building an animated "easing preview" element.

## Common gotchas
- **Never name a CustomEase the same as a built-in ease.** `CustomEase.create("power2", ...)` silently *overwrites* the built-in `power2` ease everywhere in your project — including inside other plugins and GSAP internals that may rely on it. Always pick a unique, descriptive ID (`"heroReveal"`, `"brandEase"`, `"cardSettle"`).
- **Referencing the ease before `create()` runs returns nothing usable.** If `ease: "hop"` appears in a tween that fires before `CustomEase.create("hop", ...)` has executed (e.g. due to script load order, async code, or a race in a bundler), GSAP won't find the ease and falls back to the default — the animation will run, just with the wrong timing, and nothing will throw an error to tell you why.
- **The path string is dense and easy to mistype by hand.** A single missing decimal or comma silently produces a *different* (wrong-looking) curve rather than an error — always generate the string via the Ease Visualizer or a bezier tool rather than hand-editing coordinates.
- **Normalized paths must start at `(0,0)` and end at `(1,1)`** (in the 0–1 coordinate space) to behave like a proper progress-mapping ease. A curve that doesn't span the full 0→1 range on both axes will produce a tween that doesn't actually finish at its target value smoothly.
- **CustomEase instances are global and persistent** — once created with an ID, that ID is available everywhere, including inside `gsap.timeline()` defaults, `scrollTrigger` configs, stagger eases, etc. There's no scoping or cleanup needed, but it also means duplicate IDs across files/components silently clobber each other.

## Recipes

**Define a signature "brand" ease once at page load, use it everywhere:**
```js
// near the top of your script, before any animation code runs
CustomEase.create('brandEase', 'M0,0 C0.25,0.1 0.25,1 1,1');

gsap.from('.hero-title', { opacity: 0, y: 50, duration: 0.9, ease: 'brandEase' });
gsap.from('.hero-cta',   { opacity: 0, y: 30, duration: 0.7, delay: 0.3, ease: 'brandEase' });
```

**Snappy "hop" entrance for cards on scroll (curve with overshoot baked in, so no separate bounce-back tween needed):**
```js
CustomEase.create('hop', 'M0,0 C0,0 0.056,0.442 0.175,0.442 0.294,0.442 0.332,0 0.332,0 0.332,0 0.414,1 0.671,1 0.991,1 1,0 1,0');

gsap.from('.feature-card', {
  opacity: 0, y: 80, scale: 0.9,
  stagger: 0.12, duration: 0.8, ease: 'hop',
  scrollTrigger: { trigger: '.features', start: 'top 80%' }
});
```

**Importing a curve from cubic-bezier.com directly:**
```js
CustomEase.create('softLanding', '.17,.67,.83,.67');
gsap.to('.modal', { opacity: 1, scale: 1, duration: 0.4, ease: 'softLanding' });
```

## When to skip it
If a built-in ease (`power1.out` through `power4.out`, `back.out(1.7)`, `expo.inOut`, `circ.out`, etc.) already gets you 90% of the way there, use it — built-ins are zero-setup, well-understood, and don't add a script tag. Reach for CustomEase specifically when the brand/design spec calls for a *precise, repeatable, named* curve that built-ins can't produce — not as a default for every tween.
