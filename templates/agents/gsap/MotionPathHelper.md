# MotionPathHelper

## What it's for
**This is a development tool, not an animation feature.** Reach for it only while you're *building* a `MotionPathPlugin` animation and need to visually design or fine-tune the curve in the browser by dragging anchors and control points — instead of bouncing back and forth between the page and an SVG editor like Illustrator/Inkscape. Once you're happy with the path, you copy out the path-data string it generates and hard-code that into your real tween/SVG. **It must never ship to production** — see "Common gotchas" below.

## Setup
```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/MotionPathPlugin.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/MotionPathHelper.min.js"></script>
<script>
  gsap.registerPlugin(MotionPathPlugin, MotionPathHelper);
</script>
```
**Hard dependency: MotionPathPlugin.** The docs state this explicitly — "MotionPathHelper requires MotionPathPlugin. Don't forget to load and register both plugins." There is no standalone use case.

## Key concepts
- **Two ways to invoke it**: pass it an existing tween that already has a `motionPath` defined (`MotionPathHelper.create(tween)`) to make *that* path editable, or pass it an element/selector (`MotionPathHelper.create("#id")`) to generate a brand-new basic curve from scratch that you can then sculpt.
- **It overlays an interactive editor directly on the page** — draggable anchors, control-point handles, and a big "COPY MOTION PATH" button that puts the resulting path-data string on your clipboard, ready to paste into your tween's `motionPath.path` or into an SVG `<path d="...">`.
- **It includes a looping preview animation** while you edit (configurable via `duration`/`ease` in its vars object), so you can see how the motion actually feels as you reshape the curve — not just how the curve looks statically.
- **The editing gestures are keyboard/mouse-modifier driven**: ALT-click to add a point, ALT-click an anchor to toggle smooth/corner, ALT-drag a corner anchor to pull out handles, SHIFT-click to multi-select, DELETE to remove a selected anchor, CTRL-Z to undo, and click-drag on a bare section of the path to reposition the whole thing.
- **`.kill()` tears it down** — removes the path-editing overlay and the copy button from the DOM. Useful if you're toggling the helper on/off during a dev session without a full page reload.

## Common gotchas
- **THIS MUST BE REMOVED BEFORE DEPLOY.** It injects a visible overlay UI (editable path, draggable handles, a "COPY MOTION PATH" button) directly onto the page — there is no "production mode" or auto-hide. Shipping it means real visitors see a debug tool sitting on top of your animation. Treat it exactly like `GSDevTools`: load it, use it, **delete the `<script>` tag and the `MotionPathHelper.create(...)` call** before you push to `main`.
- **It only edits — it doesn't persist.** The helper doesn't save the path data anywhere; you must explicitly click "COPY MOTION PATH" (or read the path string some other way) and paste the result into your actual production code. Closing the tab or reloading loses your edits.
- **If you pass a tween, it edits that tween's existing `motionPath` — it won't create one for you.** Make sure the tween you hand it already has a `motionPath` config; otherwise pass an element/selector instead and let the helper generate a fresh starter curve.
- **Forgetting to register `MotionPathPlugin` alongside it is a silent failure mode** — because the helper is fundamentally a UI on top of that plugin's data structures, missing the dependency tends to produce confusing errors rather than an obvious "plugin not registered" message.

## Recipes

**Design a flight path interactively, then graduate to the real animation:**
```js
// --- DEV ONLY: design the path visually ---
const tween = gsap.to(".paper-plane", {
  motionPath: { path: "#flightPath", align: "#flightPath", alignOrigin: [0.5, 0.5], autoRotate: true },
  duration: 3
});
MotionPathHelper.create(tween);
// Drag the anchors/handles until it feels right, click "COPY MOTION PATH",
// paste the resulting "M..." string into the <path d="..."> in your SVG (or
// directly into motionPath.path as a string), THEN delete this whole block.
```

**Sketch a brand-new curve from scratch for an element that has no path yet:**
```js
// --- DEV ONLY: generate and edit a starter curve ---
MotionPathHelper.create("#hero-icon", {
  pathColor: "#7c5cff",
  pathWidth: 3,
  pathOpacity: 0.6,
  duration: 2.5,
  ease: "power1.inOut"
});
// Edit, copy, paste into the real tween, then remove this block entirely.
```

## When to skip it
Always skip it in anything that reaches production — full stop. During development, you can also skip it if the path is simple enough to eyeball directly as SVG path data (e.g., a gentle arc you can write by hand with one or two cubic-bezier segments), or if you're plotting through plain `{x, y}` coordinate waypoints where `curviness` gives you "good enough" control without needing pixel-level curve sculpting.
