# InertiaPlugin

## What it's for
Reach for InertiaPlugin (formerly `ThrowPropsPlugin`) any time something needs to glide to a stop based on how fast it was *already* moving — flick-scrolling, "throw" gestures, momentum after a drag release, or any animation where the duration/landing-spot can't be hard-coded because it depends on real-time velocity. It's the plugin that makes `Draggable`'s `inertia: true` work, but it's also a fully standalone tweening tool — you can feed it any numeric property (rotation, scale, scroll position) and a velocity, and it figures out a natural-looking deceleration and duration for you.

## Setup
```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/InertiaPlugin.min.js"></script>
<!-- Almost always paired with Draggable: -->
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/Draggable.min.js"></script>
<script>
  gsap.registerPlugin(InertiaPlugin, Draggable);
</script>
```
InertiaPlugin doesn't *require* Draggable — it works fine in a plain `gsap.to()` — but the overwhelming majority of real-world use is "drag something, then let go and have it coast," so the two are normally loaded together. There's no other plugin dependency.

## Key concepts
- **It's a property of the tween config, not a separate API surface for animating**: `gsap.to(obj, { inertia: { x: 500, y: -300 } })`. Each property gets an initial *velocity* (units/second), and InertiaPlugin works out how it decelerates and where it lands.
- **The `min`/`max`/`end` options constrain the *landing spot*, not the velocity.** `{ x: { velocity: 500, max: 1024, min: 0 } }` means "start moving at 500px/s, but wherever that natural deceleration would land, clamp the final resting value between 0 and 1024." Setting `min === max` (or using `end: <number>`) forces an exact landing value; `end: [0, 100, 200]` snaps to the closest "notch"; `end: fn` lets you compute the landing value yourself.
- **Duration is computed automatically** from velocity + resistance + bounds — that's the whole point (a fast flick naturally produces a longer glide than a slow one). You can still bound it with `duration: { min, max }` if you need to keep things snappy.
- **`InertiaPlugin.track(target, "x,y")` auto-measures velocity over time** so you don't have to compute it yourself — then omit `velocity` (or set it to `"auto"`) in the inertia config and the tracked value is used automatically. **Start tracking at least ~0.5s before you need the value** — it needs a brief sampling window to gauge speed accurately.
- **Everything is reversible and scrubbable**, unlike most frame-based physics loops — because under the hood it's still a normal GSAP tween with a calculated duration/ease. Throw a bunch of inertia tweens into a timeline and `reverse()` the whole thing to watch them retrace their path.
- **It works on *any* numeric property**, not just x/y — rotation (spinning wheels), scale, scroll offsets, even method-based getter/setters. Don't think of it as "drag momentum only."

## Common gotchas
- **You must supply a `velocity` for every property unless you're using `track()`.** Omitting it (without tracking active) means InertiaPlugin has nothing to extrapolate from — the tween effectively does nothing useful. `velocity: "auto"` is a signal to pull from a tracked value, not a magic default.
- **`resistance` controls deceleration ("friction"), and tuning it is mostly trial-and-error.** There's no single "correct" value — too low and things drift forever, too high and the motion looks abrupt/mechanical rather than natural. Expect to iterate visually.
- **`linkedProps` is required for multi-axis snapping logic.** If your `end` function needs to consider both `x` and `y` together (e.g., snapping to a 2D grid point), set `linkedProps: "x,y"` so InertiaPlugin passes a combined `{x, y}` object to your function — without it, each property is evaluated independently and your function only ever sees one value at a time.
- **Tracking has a "warm-up" delay.** If you call `track()` and immediately try to read `getVelocity()` or start an inertia tween, you'll get inaccurate (often near-zero) numbers — the half-second sampling window hasn't elapsed yet.
- **Easing is ignored.** Whatever `ease` you set on the tween is irrelevant for inertia-controlled properties — InertiaPlugin computes its own deceleration curve from velocity/resistance/bounds. Don't waste time tuning an ease that won't apply.
- **Bounds (`min`/`max`) plus a fast initial velocity can overshoot before settling** — that's expected/intentional (it looks more natural than an abrupt stop), but if it looks *too* loose, that's the `overshootTolerance` knob on the Draggable side, not something you fix by tightening `min`/`max` here.

## Recipes

**Flick-scroll a panel that glides and clamps within bounds (paired with Draggable):**
```js
Draggable.create(".scroll-track", {
  type: "x",
  inertia: true,                       // hands off to InertiaPlugin automatically on release
  bounds: ".scroll-viewport",
  throwResistance: 3000
});
```

**Standalone "throw" — animate an element as if flicked, with a hard landing zone:**
```js
gsap.to(".chip", {
  duration: 1.5,
  inertia: {
    x: { velocity: 600, min: 0, max: window.innerWidth - 120 },
    y: { velocity: -250, min: 0, max: window.innerHeight - 120 },
    resistance: 600
  }
});
```

**Track velocity from a custom interaction, then let go with matching momentum:**
```js
InertiaPlugin.track(".knob", "rotation");
// ...later, on release...
gsap.to(".knob", {
  inertia: {
    rotation: { velocity: "auto", end: v => Math.round(v / 90) * 90 } // snap to 90° increments
  },
  duration: { min: 0.4, max: 2 }
});
```

## When to skip it
If you know the exact end value and duration up front — a button hover scale, a hero entrance, a scroll-triggered reveal — a plain `gsap.to()`/`gsap.from()` with a hand-picked ease (e.g. `power3.out`, `back.out`) is simpler, more predictable, and easier to art-direct. InertiaPlugin earns its keep specifically when the *landing spot and duration genuinely can't be known in advance* because they depend on user-driven velocity.
