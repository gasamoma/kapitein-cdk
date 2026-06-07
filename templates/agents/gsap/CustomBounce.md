# CustomBounce

## What it's for
Reach for CustomBounce when the built-in `"bounce"` ease feels too generic and you want a cartoonish, physically-styled drop — especially one with a synchronized "squash and stretch" effect (the classic animation principle where an object flattens on impact and stretches as it leaps). It's a thin wrapper that *generates* a matched pair of `CustomEase` curves for you (one for the bounce motion, one for the squash/stretch scale) so they land in perfect sync — something that would be extremely tedious to hand-draw as raw CustomEases.

## Setup
```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/CustomEase.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/CustomBounce.min.js"></script>
<script>
  gsap.registerPlugin(CustomEase, CustomBounce);
</script>
```
**CustomBounce extends CustomEase and requires it to be loaded and registered first** — both the `<script>` tag and the `registerPlugin()` call. Loading `CustomBounce.min.js` alone is not enough.

## Key concepts
- **`CustomBounce.create()` produces TWO eases, not one.** Calling `CustomBounce.create("myBounce", { strength: 0.6, squash: 3, squashID: "myBounce-squash" })` registers `"myBounce"` (for the bounce motion, used on `y`) AND `"myBounce-squash"` (for the squash/stretch, used on `scaleX`/`scaleY`) as CustomEase IDs you can reference by string in any tween — exactly like a normal CustomEase.
- **You always need TWO simultaneous tweens to get the full effect**: one animating `y` with the bounce ease, and a second animating `scaleX`/`scaleY` (with `transformOrigin: 'center bottom'`) using the `-squash` ease. Run them at the same time (same start position in a timeline, or just two `gsap.to()`/`gsap.from()` calls fired together).
- **`strength` controls "bounciness" (0–1), not height or distance** — it's the decay rate between bounces. A higher value (e.g. `0.9`) produces many more, closer-together bounces; a lower value (e.g. `0.3`) produces fewer, more widely-spaced ones. The actual drop height/distance is controlled entirely by the `y` value in your tween, same as any ease.
- **`squash` is a relative duration knob, not a pixel/scale amount** — it controls how long the "stuck to the ground" squash phase lasts relative to the rest of the bounce (default `0`, meaning no squash phase at all; try `2`–`4`).
- **The squash ease is a separate CustomEase with its own ID** — by default it's the bounce ID + `"-squash"` (e.g. `"hop"` → `"hop-squash"`), but you can override it explicitly with `squashID`.

## Common gotchas
- **Forgetting `squash` entirely means no squash ease is generated that's meaningfully different from a no-op** — `squash` defaults to `0`. If you want the squash/stretch effect (and not just the bounce motion), you must explicitly set `squash` to a positive number (e.g. `2` or `3`).
- **The squash tween needs `transformOrigin: 'center bottom'`** (or wherever your element's "ground contact point" is) — without it, the scale animation will stretch the element from its center, which looks wrong for an object squashing against a surface below it.
- **`scaleY` should generally move opposite to `scaleX`** in the squash tween (e.g. `scaleX: 1.4, scaleY: 0.6`) to read as a believable squash — animating only one axis looks like simple stretching, not impact compression.
- **`endAtStart: true` changes the *shape* of the whole curve**, not just where it ends — it produces a "leap up, then bounce back down to rest at the starting point" arc rather than a straight "fall and settle" arc. Don't reach for it expecting a subtle tweak; it fundamentally changes what kind of motion you get. Make sure your tween's `y` values match the motion you actually want (e.g. animating `y` *up* to a negative value with `endAtStart: true` for a "jump" look vs. animating `y` *down from* a negative value for a "drop" look).
- **You can also use the condensed string syntax** (`ease: "bounce(0.5)"` or `ease: "bounce({strength:0.5, endAtStart:true})"`) directly in a tween *as long as CustomBounce has been loaded and registered* — this skips the explicit `.create()` + named-ID step but only works for the bounce motion itself, not the squash pairing.

## Recipes

**Element drops in and bounces to rest (bounce only, no squash — simplest case):**
```js
CustomBounce.create('dropIn', { strength: 0.6 });

gsap.from('.notification-toast', {
  y: -300,
  duration: 1.4,
  ease: 'dropIn',
  scrollTrigger: { trigger: '.notification-toast', start: 'top 85%' }
});
```

**Cartoon mascot/icon lands with full squash-and-stretch (the showcase use case):**
```js
CustomBounce.create('mascotLand', {
  strength: 0.6,
  squash: 3,
  squashID: 'mascotLand-squash'
});

const tl = gsap.timeline({ scrollTrigger: { trigger: '.mascot', start: 'top 75%' } });
tl.from('.mascot', { y: -240, duration: 1.6, ease: 'mascotLand' }, 0)
  .to('.mascot', {
    scaleX: 1.3, scaleY: 0.7,
    transformOrigin: 'center bottom',
    duration: 1.6, ease: 'mascotLand-squash'
  }, 0);
```

**CTA button "pops" up into view and settles (using `endAtStart` for a leap-and-land feel):**
```js
CustomBounce.create('ctaPop', { strength: 0.5, endAtStart: true });
gsap.from('.hero-cta', { y: -40, duration: 1, ease: 'ctaPop', delay: 0.6 });
```

## When to skip it
If you just need "a bit of bounce" on a settle, GSAP's built-in `"bounce.out"` ease is one word and zero setup — use it. Reach for CustomBounce only when (a) the built-in bounce's rhythm/strength doesn't match your design, or (b) you specifically want the squash-and-stretch pairing, which the built-in simply can't produce. It's a "delight" detail best used sparingly — once per page (hero mascot, a single CTA, an empty-state illustration), not on every card in a grid.
