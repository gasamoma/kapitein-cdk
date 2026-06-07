# PhysicsPropsPlugin

## What it's for

Reach for PhysicsPropsPlugin when you want a property to move based on **velocity/acceleration/friction** rather than a destination value and easing curve — "throw this at 200px/sec and let it decelerate" instead of "animate this to x:200 over 1s with ease power2.out". It's the generalized sibling of `Physics2DPlugin` (which is specifically x/y position with gravity): PhysicsPropsPlugin can drive *any* numeric property — CSS values, SVG attributes, generic object properties — using the same physics model. Use it when the natural description of the motion is in terms of "how fast" and "how it decays," not "where it ends up."

## Setup

```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/PhysicsPropsPlugin.min.js"></script>
<script>
  gsap.registerPlugin(PhysicsPropsPlugin);
</script>
```

No required dependencies. It's conceptually paired with `Physics2DPlugin` (2D position + gravity/friction — reach for that one first if you're doing confetti/particle bursts on x/y) and with `InertiaPlugin` (momentum after a `Draggable` release — different mechanism, similar "feel"). Pick PhysicsPropsPlugin specifically when you need physics-driven motion on a property that ISN'T simply 2D position.

## Key concepts

- **You provide motion parameters, not a destination.** The whole point is that you *don't* need to know (or care) where the value ends up — you describe how it starts moving and how that decays, and the plugin computes the resulting curve.
- **Per-property physics object.** Based on the plugin's TypeScript definitions and community examples, you nest physics parameters under a `physicsProps` object keyed by the property name, e.g. `physicsProps: { x: { velocity: 100 }, rotation: { velocity: 50, acceleration: -20 } }` — each animated property gets its own independent velocity/acceleration/friction. *(This nested-per-property structure is corroborated by community examples; the official docs page documents the parameters themselves but is light on full usage syntax — verify against `Physics2DPlugin`'s docs, which follow the same conventions, if you need more confidence before shipping.)*
- **`ease` is ignored for physics-driven properties.** The physics parameters (`velocity`, `acceleration`, `friction`) determine the motion curve entirely — any `ease` you set on the tween has no effect on these properties. This trips people up coming from normal tweens where ease is assumed to always apply.
- **Everything is reversible**, including friction-based deceleration — wrap physics tweens in a timeline and `reverse()` it to watch objects retrace their path back to the start. This is a genuinely unique convenience versus hand-rolling physics.
- **`friction` is a 0–1 "feel" dial, not a scientific unit.** `0` = none, `~0.08` = light, `1` = effectively frozen. The docs explicitly say it's not meant to be precise/scientific — treat it as "experiment until it feels right," starting around `0.02` for subtle effects.

## Common gotchas

- **Friction costs more to compute.** The official docs explicitly note that physics tweens *with* friction require more processing than those without — if you're animating many elements simultaneously (e.g. a particle burst), consider whether you actually need friction on all of them, or whether a cheaper `Physics2DPlugin` gravity-only setup would do.
- **Parameters are fixed at tween creation — don't expect to tweak them mid-flight.** The docs note these aren't meant to be dynamically updateable; if you need different physics behavior, create a new tween rather than mutating an existing one's `physicsProps`.
- **Because there's no destination value, you can't "land" an element precisely with this plugin alone.** If your design needs the motion to *end* at a specific spot (e.g. a card settling into a grid position), you'll likely need to follow up with a regular `gsap.to()` tween to the exact final values, or reconsider whether `Physics2DPlugin` (which does support an end-state via gravity settling) is a better fit.
- **This is a genuinely niche plugin** — the official documentation page itself is unusually thin (a description, a parameter table, and a link to demos), which suggests GreenSock considers it a "for advanced/specific cases" tool rather than a everyday building block. Don't feel obligated to reach for it; most "should feel physical" landing-page effects are well served by `Physics2DPlugin` (bursts/falls) or a well-chosen `ease` like `"elastic"` / `"back"` / `"bounce"`.

## Recipes

**Floating decorative element with organic drift (velocity + light friction, no destination):**
```js
gsap.to('.floating-orb', {
  duration: 4,
  physicsProps: { x: { velocity: 60, friction: 0.05 }, y: { velocity: -40, friction: 0.05 } }
});
```

**Icon "flick" on hover that settles back via reverse (showcasing the reversibility):**
```js
const flickTl = gsap.timeline({ paused: true });
flickTl.to('.icon', {
  duration: 1.2,
  physicsProps: { rotation: { velocity: 180, friction: 0.06 } }
});

iconEl.addEventListener('mouseenter', () => flickTl.restart());
iconEl.addEventListener('mouseleave', () => flickTl.reverse());
```

## When to skip it

For confetti, particle bursts, or anything that's fundamentally "launch and fall under gravity" on x/y, use `Physics2DPlugin` — it's purpose-built for that and has a more complete, better-documented API (including launch angle/gravity that produces natural arcs). For momentum after a drag-and-release interaction, use `InertiaPlugin` with `Draggable`. And if the motion has a clear destination and a "feel" you can describe with a named ease (snappy, bouncy, elastic, gentle), a plain `gsap.to()` with the right `ease` string is simpler, cheaper, and more predictable than physics simulation — reserve PhysicsPropsPlugin for the rare case where "how it moves" genuinely matters more than "where it ends up."
