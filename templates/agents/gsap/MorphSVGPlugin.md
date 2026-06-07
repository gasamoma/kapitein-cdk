# MorphSVGPlugin

## What it's for

Reach for MorphSVG when one SVG shape needs to smoothly become a *different* shape — logo states transitioning, icon A turning into icon B, decorative blobs shifting form in the background. It rewrites the path's `d` attribute over time with genuine shape interpolation (not a crossfade), and it's notably tolerant of mismatched point counts/types between start and end shapes — most other morphing approaches require carefully matched artwork. Don't reach for it just to reveal a shape (`DrawSVGPlugin`) or to move/scale/rotate a shape (plain `gsap.to()` on transforms).

## Setup

```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/MorphSVGPlugin.min.js"></script>
<script>
  gsap.registerPlugin(MorphSVGPlugin);
</script>
```

No dependencies on other plugins, though it's commonly combined with `DrawSVGPlugin` (e.g. draw a shape in, then morph it) or used alongside `MorphSVGPlugin.convertToPath()` to prep `<rect>`/`<circle>`/`<ellipse>`/`<polygon>`/`<polyline>`/`<line>` elements that DrawSVG itself struggles to render correctly.

## Key concepts

- **You're animating the `d` attribute of a `<path>`, not a transform.** This is fundamentally different from transform/opacity animation — it's GPU-unfriendly string interpolation happening on every tick. Use it deliberately and sparingly (hero moments, not scroll-linked backgrounds with dozens of instances).
- **Targets can be a selector, an element reference, or raw path-data string** — `morphSVG: "#otherShape"` grabs the `d` from that element; `morphSVG: "M47.1,0.8..."` uses literal path data directly. Non-path shapes (`<circle>`, `<rect>`, etc.) get auto-converted to path data internally when referenced this way.
- **`shapeIndex` controls *where* each shape's point sequence "starts."** Every closed path has an arbitrary starting point (think of tracing a circle — you can start at 12 o'clock or 3 o'clock). If the start/end shapes' point sequences begin in different places, the morph can visually "invert" or twist through itself mid-animation. `shapeIndex` is the offset that re-aligns them; the `findShapeIndex()` dev utility helps you find the right number experimentally.
- **`type: "rotational"` vs default `"linear"` interpolation** — linear interpolates raw x/y coordinates (usually fine), but rotational interpolates angle+length instead, which can eliminate odd "kinks" forming in smooth curves mid-morph. New in 3.14: `curveMode: true` is a related (but distinct) option that smooths anchor-handle interpolation specifically to avoid kinks — try it before reaching for `type: "rotational"` if linear morphs look slightly "broken" through curves.
- **The original shape is preserved on the element** (`data-original` attribute), so morphing back to the start is as simple as targeting the element's own original ID/selector again in a later tween.

## Common gotchas

- **Only `<path>`, `<polygon>`, and `<polyline>` can be morphed directly.** `<circle>`, `<rect>`, `<ellipse>`, and `<line>` get converted to path data automatically *when passed as the `morphSVG` value*, but if you need to animate one of THOSE elements directly (as the tween target), call `MorphSVGPlugin.convertToPath("circle, rect, ellipse, line, polygon, polyline")` first — it swaps the DOM element for an equivalent `<path>`, preserving attributes like `id`, so your selectors keep working.
- **Mismatched visual complexity can cause unexpected twisting** even with MorphSVG's flexible point-matching — if a morph looks like it's crossing over itself, that's the `shapeIndex` alignment issue described above, not a bug. Reach for `findShapeIndex()` during development rather than guessing.
- **`smooth` redraws the path by default**, which can subtly change fidelity to the original artwork (it's "tracing at a resolution" to evenly distribute anchor points). If preserving exact original geometry matters, use the object form `smooth: { points: N, redraw: false }`.
- **Performance cost scales with path complexity.** For very complex shapes, the *initial* calculation (matching/reorganizing points) can be expensive enough to cause a jank on first render. The documented fix is `precompile`, which runs those calculations ahead of time and lets you paste the precomputed strings directly into the tween — only worth doing if you actually observe a stutter.
- **Defining `shapeIndex` numerically up front skips the "auto" matching calculations**, which is the single biggest performance win for repeated/complex morphs — `shapeIndex: "auto"` (the default) is convenient but does real work on every run.

## Recipes

**Logo mark morphing into an alternate state on hover/load:**
```js
const tl = gsap.timeline({ defaults: { duration: 0.8, ease: 'power2.inOut' } });
tl.to('#logo-mark', { morphSVG: '#logo-mark-alt' });
// .to('#logo-mark', { morphSVG: '#logo-mark' }, '+=2') // morph back to original
```

**Icon state change triggered by a UI interaction (e.g. menu open/close):**
```js
function toggleMenuIcon(isOpen) {
  gsap.to('#menu-icon-path', {
    duration: 0.5,
    ease: 'power2.inOut',
    morphSVG: isOpen ? '#close-icon-shape' : '#hamburger-shape'
  });
}
```

**Sequenced "shape showcase" — one path cycling through several forms:**
```js
const tl = gsap.timeline({ repeat: -1, repeatDelay: 1 });
tl.to('#blob', { duration: 1.2, morphSVG: '#blob-2', ease: 'power2.inOut' })
  .to('#blob', { duration: 1.2, morphSVG: '#blob-3', ease: 'power2.inOut' }, '+=1')
  .to('#blob', { duration: 1.2, morphSVG: '#blob', ease: 'power2.inOut' }, '+=1'); // back to original
```

## When to skip it

If you only need a shape to move, scale, rotate, or fade — not change its actual outline — plain `gsap.to()` with transform/opacity is lighter and GPU-accelerated; don't reach for path-data interpolation for things transforms already do well. If you want a stroke to progressively reveal along a *fixed* shape (no shape change), that's `DrawSVGPlugin`. And because morphing genuinely costs CPU on every tick, avoid using it for ambient/looping background decoration where dozens of instances would run simultaneously — pick one hero moment and let it shine there.
