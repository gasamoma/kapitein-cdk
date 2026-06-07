# MotionPathPlugin

## What it's for
Reach for MotionPathPlugin whenever something needs to travel along a *curve* rather than a straight line — flying icons/objects, orbiting elements, characters walking a winding road, hero entrances that swoop in along an arc, or any "fly from A to B but make it interesting" moment. It's also useful for smoothing velocity through a *sequence of values* (not just x/y coordinates) — e.g., animating scale/rotation through several waypoints with natural easing between them.

## Setup
```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/MotionPathPlugin.min.js"></script>
<script>
  gsap.registerPlugin(MotionPathPlugin);
</script>
```
No required dependencies. It pairs naturally with **MotionPathHelper** during development (visually edit the path, copy the data, then remove the helper before deploy — see that plugin's doc) and with ScrollTrigger if you want the journey along the path to be scroll-scrubbed.

## Key concepts
- **It's a tween property, used like any other**: `gsap.to(target, { motionPath: { path: "#path", ... }, duration: 4 })`. Under the hood it's still a normal GSAP tween — everything else (`ease`, `duration`, `repeat`, `stagger`, timelines) works exactly as you'd expect.
- **`path` accepts four different shapes of input**: a reference/selector to an SVG `<path>` (`"#pathID"`), a raw SVG path-data string (`"M9,100c0,0,18-41,49-65"`), an array of `{x, y}` coordinates (GSAP plots a smooth curve through them — control "curviness" with `curviness`), or an array of arbitrary property objects like `[{scale: 0.5, rotation: 10}, {scale: 1, rotation: -10}]` to smooth velocity through non-positional values.
- **`align` is the "magic" that makes this actually usable in real layouts.** Without it, raw path coordinates are just plugged into the target's x/y transforms — which only lines up if target and path share the exact same coordinate space. `align: "#pathID"` (or `align: "self"`) bends the coordinate systems so the target sits exactly on the path regardless of how deeply nested either one is in transformed containers. Combine with `alignOrigin: [0.5, 0.5]` to center the target on the path rather than aligning its top-left corner.
- **`autoRotate` orients the element to the path's direction of travel.** `true` matches the path angle exactly; a number (e.g. `autoRotate: 90`) adds a fixed offset — handy when your art asset's "forward" isn't pointing right. Pair it with `transformOrigin: "50% 50%"` so rotation pivots around the element's center, not its corner.
- **`start`/`end` (0–1 progress values) let you animate along a *segment* of the path**, including going backwards (`end < start`) or wrapping past 1 to loop. Default is the full path (`start: 0, end: 1`).
- **Helper methods turn this into a coordinate-conversion toolkit, not just a path-walker**: `convertCoordinates()`, `getGlobalMatrix()`, `getRelativePosition()` calculate exact positions between elements across nested transforms — useful for "move element A to exactly where element B is" without Flip.

## Common gotchas
- **Alignment is calculated ONCE at tween start — it is NOT responsive.** If the viewport resizes (or anything shifts the path's position) mid-animation, the alignment won't recalculate; the docs explicitly call this out as intentional (recalculating every tick would be too expensive). If you need resize-safety, record `progress()`, kill the tween, and recreate it with the recorded progress on resize.
- **The path element must actually exist in the DOM and be addressable by the selector you pass** — if `path: "#pathID"` can't find a match, the tween silently has nothing to follow. Double-check the SVG `<path>` is rendered (not `display: none` at the time of tween creation) before wiring up the animation.
- **`autoRotate` needs the right `transformOrigin` to look natural.** Forgetting `transformOrigin: "50% 50%"` (or setting `xPercent: -50, yPercent: -50` alongside `alignOrigin: [0.5, 0.5]`) is the most common reason a rotating element looks like it's "wobbling around a corner" instead of smoothly banking into turns.
- **Curviness only applies to coordinate-array paths, not SVG `<path>` data.** If you're plotting through raw `{x, y}` waypoints and the curve looks too sharp or too loose, that's the `curviness` knob (`0` = straight segments/hard corners, `1` = default smooth curve, `2`+ = exaggeratedly curvy) — it has no effect when you supply actual SVG path data or a `<path>` reference.
- **`fromCurrent` defaults to `true`**, meaning the target's *current* position is automatically prepended to a coordinate-array path so the motion starts smoothly from wherever it already is. If you actually want it to jump straight to the first defined point, set `fromCurrent: false` explicitly — otherwise you'll see an unexpected "extra" leg at the start of the journey.
- **`useRadians` defaults to `false` (degrees).** If you're feeding rotation values into something that expects radians (e.g. coordinating with a Pixi.js/canvas layer), forgetting to set `useRadians: true` produces wildly wrong rotation math.

## Recipes

**Hero icon flying in along a curved entrance (respects transform/opacity-only rule):**
```js
gsap.set(".hero-icon", { opacity: 0 });
gsap.to(".hero-icon", {
  opacity: 1,
  motionPath: {
    path: [
      { x: -200, y: 120 },
      { x: -80, y: -40 },
      { x: 0, y: 0 }      // lands at its natural position
    ],
    curviness: 1.4
  },
  duration: 1.2,
  ease: "power2.out"
});
```

**Element gliding along a designed SVG path with auto-rotation (a "fly to the CTA" moment):**
```js
gsap.to(".paper-plane", {
  motionPath: {
    path: "#flightPath",
    align: "#flightPath",
    alignOrigin: [0.5, 0.5],
    autoRotate: true
  },
  transformOrigin: "50% 50%",
  duration: 3,
  ease: "power1.inOut",
  scrollTrigger: { trigger: "#hero", start: "top top", end: "bottom top", scrub: 1 }
});
```

**Looping orbit (decorative background element circling a point):**
```js
gsap.to(".orbit-dot", {
  motionPath: {
    path: "#orbitCircle",
    align: "#orbitCircle",
    alignOrigin: [0.5, 0.5],
    end: 1            // full loop
  },
  duration: 8,
  ease: "none",
  repeat: -1
});
```

## When to skip it
For straight-line moves, fades, scales, or staggered reveals, plain `gsap.to()`/`gsap.from()` is simpler and has less overhead — don't reach for a path just to move something from point A to point B in a line. And if the goal is morphing the *shape* of an SVG path (not moving an element along it), that's MorphSVGPlugin's job, not this one.
