# Draggable

## What it's for
Reach for Draggable whenever the user needs to physically grab and move something with a mouse/touch — sliders, carousels, custom scrollbars, swipeable cards, draggable panels, spinnable dials/wheels. It's the right call any time the interaction is "press, move, release" rather than a scripted/triggered animation. It's not for things that merely *animate* on scroll or hover — that's ScrollTrigger/Observer territory.

## Setup
```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/Draggable.min.js"></script>
<!-- Add InertiaPlugin too if you want flick-and-coast momentum after release -->
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/InertiaPlugin.min.js"></script>
<script>
  gsap.registerPlugin(Draggable, InertiaPlugin);
</script>
```
Draggable has no hard dependency on InertiaPlugin, but the two are designed to work together: load InertiaPlugin and simply set `inertia: true` in the Draggable config to get natural momentum/coasting after release — no extra wiring required. **Load order matters**: register `gsap` first, then `Draggable`, then `InertiaPlugin` (the order shown above is the documented/recommended one).

## Key concepts
- **`Draggable.create(target, vars)` returns an array of Draggable instances**, not a single one (a selector can match multiple elements). Grab `const [drag] = Draggable.create(...)` if you need to reference it later.
- **`type` determines what dragging actually controls**: `"x,y"` (default, uses transforms — GPU-accelerated), `"x"`/`"y"` for single-axis, `"top,left"` for layout-based positioning, or `"rotation"` to make something spinnable. Pick the type that matches the visual effect — don't fight it with CSS constraints.
- **`bounds` constrains where the element can go** — pass a container selector/element (`bounds: "#container"`), a rectangle (`bounds: {top, left, width, height}`), or min/max values (`bounds: {minRotation: 0, maxRotation: 270}`). Without bounds, elements can be dragged anywhere, including off-screen.
- **`inertia: true` is the bridge to InertiaPlugin** — it auto-generates a momentum tween on release using the tracked velocity. Once that's on, a cluster of related options (`throwResistance`, `maxDuration`, `minDuration`, `overshootTolerance`, `onThrowUpdate`, `onThrowComplete`) become available and meaningful.
- **`this` inside callbacks is the Draggable instance**, giving you direct access to `this.target`, `this.x`/`this.y`, and bounds info (`this.maxX`, `this.minX`, `this.maxY`, `this.minY`) — very useful for building custom snap/clamp logic in `onDrag`/`onDragEnd`.
- **Snapping comes in two flavors**: `snap` (applies only to where the element *lands* after release — works with InertiaPlugin to compute the natural resting spot, then nudge it to the nearest valid value) vs. `liveSnap` (applies continuously *while* dragging, e.g. snapping to a grid in real time).

## Common gotchas
- **Clicks on `<a>`, `<button>`, `<input>`, `<select>`, `<textarea>` (and anything with `data-clickable="true"`) don't trigger dragging by default** — Draggable assumes you want native click/focus behavior on those. If your draggable card contains a CTA button that isn't responding, that's why; set `dragClickables: true` to override, or provide a custom `clickableTest` function for fine-grained control.
- **`onClick` only fires if the pointer moved less than ~3px** (configurable via `minimumMovement`); `onDragEnd` *always* fires on release regardless of movement. Don't rely on `onDragEnd` to detect "was this a tap or a drag" — use `onClick` for that, or check the distance yourself.
- **`inertia: true` silently does nothing if InertiaPlugin isn't loaded/registered** — there's no error, the element just stops dead on release instead of coasting. If momentum "isn't working," check the script tag and `registerPlugin` call first.
- **Bounds and inertia can fight each other.** A fast flick can carry the element past its bounds before InertiaPlugin's deceleration kicks in (community-reported: "inertia ignores bounds and flies offscreen"). Tune `edgeResistance` (resistance while dragging past the boundary) and `overshootTolerance` (how far the inertia tween is allowed to overshoot before easing back) together — don't assume `bounds` alone constrains a thrown element.
- **`type: "x,y"` uses CSS transforms — verify your CSS isn't also setting `top`/`left`/`position` in a way that conflicts.** Mixing transform-based dragging with layout-based positioning on the same element produces jittery, fighting movement.
- **Rotation pivots around the element's center by default.** If you need a different pivot for a `type: "rotation"` drag (e.g., rotate around a corner like a clock hand), set `transformOrigin` via `gsap.set()` *before* creating the Draggable — Draggable honors whatever `transformOrigin` is already on the element.
- **`force3D` is on by default**, putting the dragged element on its own GPU layer (good for perf) — but if the element has animating children, that can sometimes cause flicker/compositing artifacts; `force3D: false` is the documented escape hatch.

## Recipes

**Horizontal carousel/slider that coasts to a stop on flick:**
```js
const [carousel] = Draggable.create(".carousel-track", {
  type: "x",
  bounds: ".carousel-viewport",
  inertia: true,
  edgeResistance: 0.65,
  throwResistance: 4000,
  snap: {
    x: gsap.utils.snap(slideWidth)   // land on the nearest slide boundary
  },
  onDragStart: function () { this.target.classList.add("is-dragging"); },
  onDragEnd:   function () { this.target.classList.remove("is-dragging"); }
});
```

**Draggable card stack that only moves via its header (trigger element):**
```js
Draggable.create(".panel", {
  type: "x,y",
  trigger: ".panel-header",
  bounds: "#workspace",
  edgeResistance: 0.85,
  inertia: true,
  zIndexBoost: true,           // bring the grabbed panel to the front automatically
  cursor: "grab",
  activeCursor: "grabbing"
});
```

**Spinnable dial that snaps to 90° increments after release:**
```js
Draggable.create("#dial", {
  type: "rotation",
  inertia: true,
  snap: value => Math.round(value / 90) * 90
});
```

## When to skip it
If the "movement" is purely scripted (no user grabbing involved) — parallax, scroll-linked reveals, hover states — you don't need Draggable at all; use plain tweens or ScrollTrigger/Observer. And if you only need to *detect* swipe direction/velocity (not actually move an element with the pointer), Observer is lighter-weight and purpose-built for that.
