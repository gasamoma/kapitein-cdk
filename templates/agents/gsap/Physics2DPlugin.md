# Physics2DPlugin

## What it's for
Reach for Physics2DPlugin whenever you want elements to move the way real objects do under gravity/thrust/drag — confetti bursts, particle explosions, falling/scattering elements, fireworks, things that get "launched" and arc back down. It's the simplest way to get a convincing parabolic arc or scatter effect without hand-animating x/y keyframes or writing your own physics loop. The docs are explicit that it's *not* a full physics engine — no collision detection — it's a convenience layer for tweening x/y based on velocity, angle, gravity, acceleration, and friction.

## Setup
```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/Physics2DPlugin.min.js"></script>
<script>
  gsap.registerPlugin(Physics2DPlugin);
</script>
```
No required dependencies. It's commonly used with `gsap.utils.random()` / `gsap.timeline({stagger: ...})` to vary each particle's launch angle/velocity so a burst doesn't look mechanically uniform, and often combined with a fade-out tween on `opacity` so particles disappear gracefully rather than stopping abruptly.

## Key concepts
- **It's a tween-config property, just like `motionPath` or `inertia`**: `gsap.to(el, { duration: 2, physics2D: { velocity: 300, angle: -60, gravity: 400 } })`. Everything else about the tween (`duration`, `stagger`, `repeat`, callbacks) behaves like any normal GSAP tween.
- **`velocity` + `angle` define the launch**: velocity is speed in pixels/second, angle is the direction of travel in degrees (e.g., `-60` = up and to the right, since 0° is to the right and negative angles go "up" in screen coordinates). Nothing moves without an initial `velocity`.
- **`gravity` is just a convenience wrapper around `acceleration` + `accelerationAngle: 90`.** The docs say it plainly: "gravity is the same thing as acceleration applied at an accelerationAngle of 90 ... think of gravity as a convenience property that automatically sets the accelerationAngle for you." Use `gravity` for the common "things fall down" case; reach for `acceleration`/`accelerationAngle` directly only when you need a *different* constant force direction (e.g., wind blowing sideways). **You cannot combine both** — they're mutually exclusive ways of expressing the same underlying mechanic.
- **`friction` is a 0–1 "feel" knob, not a scientific value.** `0` = none, `~0.08` = light drag, `1` = nearly frozen. The docs explicitly recommend starting tiny (`0.02`) and nudging from there — there's no "correct" number, only what looks right for your effect. Friction also costs more processing than physics tweens without it.
- **`xProp`/`yProp` let you redirect the simulation onto different properties** — default is `x`/`y` (transforms), but you can target `left`/`top` if your layout demands it (though per the project's hard rule, prefer transform-based `x`/`y` for performance).
- **Like InertiaPlugin, the whole thing is reversible** — throw a batch of physics tweens into a timeline and `reverse()` it to watch particles retrace their arcs back to origin. Also note: **whatever `ease` you set on the tween is ignored** — the physics math drives the motion entirely.

## Common gotchas
- **Forgetting `velocity` means nothing moves** — without an initial speed there's no motion to simulate; `gravity`/`acceleration` alone won't kick something off from a standstill in this plugin (unlike a real physics engine where gravity alone would eventually move a resting object).
- **`gravity` and `acceleration` are mutually exclusive** — setting both is contradictory (gravity *is* acceleration at a fixed angle); pick one mental model and stick with it for a given tween.
- **Friction adds real per-frame processing cost.** For large bursts (50+ particles), test performance with friction enabled — if things start chugging, consider dropping friction and relying on `gravity` + a capped `duration` plus an opacity fade-out to mask the stop instead.
- **The `duration` you set is a hard ceiling, not a simulation outcome** — the tween still ends exactly when its `duration` elapses, so you need to choose a duration that lets the arc complete naturally (long enough for gravity to bring it back down) or deliberately cut it short for a "burst that fades mid-flight" look.
- **Angle convention can surprise people coming from math/physics contexts**: 0° points right, and because screen Y increases *downward*, "upward" launches use *negative* angles (e.g., `-60` to `-120` for "up and outward" confetti). Sketch it out before guessing.
- **Pair with `opacity` fade-outs for a polished finish** — particles that simply vanish when the tween ends look abrupt; animating `opacity` to `0` over the tail end of the duration (or in a separate concurrent tween) reads as much more natural and respects the project's transform/opacity-only performance rule.

## Recipes

**Confetti burst from a button/CTA on success (staggered launch angles + fade):**
```js
function burstConfetti(originEl, count = 24) {
  const pieces = gsap.utils.toArray(originEl.querySelectorAll(".confetti-piece"));
  pieces.forEach((piece, i) => {
    gsap.set(piece, { opacity: 1, x: 0, y: 0 });
    gsap.to(piece, {
      duration: gsap.utils.random(1.2, 1.8),
      physics2D: {
        velocity: gsap.utils.random(250, 450),
        angle: gsap.utils.random(-110, -70),   // mostly "up", spread outward
        gravity: 600
      },
      opacity: 0,                              // fades out as it falls — masks the abrupt stop
      ease: "none",
      delay: i * 0.015
    });
  });
}
```

**Falling/scattering elements (e.g., icons tumbling away on a state change):**
```js
gsap.utils.toArray(".scatter-item").forEach(el => {
  gsap.to(el, {
    duration: 1.4,
    physics2D: {
      velocity: gsap.utils.random(80, 200),
      angle: gsap.utils.random(60, 120),       // generally downward
      gravity: 500,
      friction: 0.04
    },
    opacity: 0,
    rotation: gsap.utils.random(-180, 180)     // tumbling — combine freely with physics2D
  });
});
```

## When to skip it
If you just need a single element to travel along a *designed* curve (a hero icon swooping into place, an orbiting decoration), `MotionPathPlugin` gives you precise art-directed control that physics simulation can't — physics is great for "looks chaotic/organic" but bad for "lands exactly here." And if you need forces applied to properties *other than position* (e.g., physics-driven color shifts or arbitrary CSS values), that's `PhysicsPropsPlugin`'s job, not this one.
