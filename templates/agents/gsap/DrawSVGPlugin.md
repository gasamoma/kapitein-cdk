# DrawSVGPlugin

## What it's for

Reach for DrawSVG when you want an SVG stroke to appear to "draw itself" — line-art logos, signature animations, icon outlines tracing in, underline accents appearing beneath headlines. It works by animating `stroke-dashoffset`/`stroke-dasharray` (both pure paint properties, not layout), which makes it a perfectly performance-safe complement to the project's transform/opacity rule. Don't use it to animate fills or shape geometry — that's `MorphSVGPlugin`'s job.

## Setup

```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/DrawSVGPlugin.min.js"></script>
<script>
  gsap.registerPlugin(DrawSVGPlugin);
</script>
```

No dependencies on other plugins. Pairs naturally with `ScrollTrigger` (draw on scroll-into-view) and timelines (sequence multiple strokes drawing in order).

## Key concepts

- **The `drawSVG` value describes the END STATE (or start state, for `from()`), not a range to animate between.** `gsap.to("#path", { drawSVG: "20% 80%" })` animates *toward* a stroke that spans 20%–80% of the path — from wherever the stroke currently is. It does not mean "animate the values from 20 to 80."
- **A `drawSVG` value is actually two numbers: a start and end position along the path.** `"100%"` is shorthand for `"0% 100%"` (draw the whole thing from the beginning). Because you control both ends, you can do far more than a simple "wipe in" — animate a segment from the middle outward (`"50% 50%"` → `"0% 100%"`), or slide a fixed-length dash along the whole path.
- **You must already have a visible stroke before animating it.** DrawSVG manipulates `stroke-dasharray`/`stroke-dashoffset`, but if the element has no `stroke`/`stroke-width` (via CSS or SVG attributes), there's nothing to reveal — the animation will run with no visible effect.
- **Percentages vs. absolute lengths** — you can mix either; percentages are usually easier to reason about and remain correct if the path's geometry changes.
- **`"live"` suffix recalculates path length every tick** — only needed in the rare case where the SVG's geometry actually changes mid-animation (e.g. a responsive resize affecting the path), since recalculating every frame costs more.

## Common gotchas

- **Multi-segment `<path>` elements (multiple `M` commands) render strokes unreliably across browsers.** Prefer single-segment paths. If your artwork has multiple subpaths, GSAP's docs point to a helper that splits a multi-segment path into one `<path>` per segment — do that *before* animating rather than fighting inconsistent rendering.
- **Firefox sometimes under-calculates path length**, causing the stroke to visibly stop short of 100% even when you animate to `"100%"`. The documented workarounds are either adding more anchor points so control points hug the path more closely, or simply overshooting slightly (e.g. `"102%"` instead of `"100%"`) — this is a Firefox quirk, not a DrawSVG bug.
- **iOS Safari has historically misrendered `<rect>` strokes** (too thick, artifacts, misplaced origin). If you hit this, convert the `<rect>` to a `<path>` or `<polyline>` — `MorphSVGPlugin.convertToPath()` can do this conversion for you if that plugin is also loaded.
- **`<use>` elements cannot be visually affected** — browsers don't allow modifying the rendered contents of a `<use>` reference, so DrawSVG tweens on them will run without producing any visible change. Animate the original element instead.
- **DrawSVG only affects the stroke, never the fill.** If your design calls for a shape that both draws its outline AND fills in, you need a second tween (e.g. animating `fillOpacity` or `opacity` on the fill) sequenced after or alongside the draw — DrawSVG alone won't produce that.

## Recipes

**Logo/icon line-drawing reveal on scroll:**
```js
gsap.from('.logo-path', {
  drawSVG: 0,                 // start fully hidden, animate "to" the path's natural full state
  duration: 1.4,
  ease: 'power2.inOut',
  scrollTrigger: { trigger: '.logo-path', start: 'top 85%', once: true }
});
```

**Staggered multi-stroke icon set drawing in sequence:**
```js
gsap.from('.draw-me', {
  drawSVG: 0,
  duration: 1,
  stagger: 0.15,
  ease: 'power1.out',
  scrollTrigger: { trigger: '.icon-row', start: 'top 80%' }
});
```

**Animated underline accent beneath a heading (draws from center outward):**
```js
gsap.fromTo('.underline-path',
  { drawSVG: '50% 50%' },
  {
    drawSVG: '0% 100%',
    duration: 0.8,
    ease: 'power2.out',
    scrollTrigger: { trigger: '.underline-path', start: 'top 90%', once: true }
  }
);
```

## When to skip it

If the "drawing" effect you want is really just a shape fading or scaling into view, plain `gsap.from()` on `opacity`/`scale` is simpler and avoids loading an extra plugin. If you need the SVG shape itself to morph from one form into another (not reveal a stroke along an existing path), that's `MorphSVGPlugin`. And if your icon is a simple raster image or icon font glyph rather than an SVG with a meaningful stroke path, DrawSVG has nothing to offer — animate it with transform/opacity instead.
