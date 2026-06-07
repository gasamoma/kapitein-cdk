# GSAP Core (gsap.min.js)

## What it's for
The core engine — `gsap.to/from/fromTo/set`, Timelines, easing, staggers, and utility helpers. Reach for it directly for any property animation; reach for a Timeline (not chained `delay`s) the moment you have more than one or two animations that need to relate to each other in time.

## Setup
```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/gsap.min.js"></script>
```
No registration needed for the core — it's always loaded first. Plugins (`ScrollTrigger`, `SplitText`, etc.) extend this object via `gsap.registerPlugin(...)`.

## Key concepts
- **Tweens are property setters, not "animations you configure once."** `gsap.to(target, {x: 100, duration: 1})` reads the *current* value and animates to the destination — you never need to specify a starting value. `from()` does the reverse (animates *from* the given values to the current ones); `fromTo()` lets you lock down both ends explicitly.
- **Timelines are containers, not animators.** A `Timeline` never sets a single property itself — it just controls when its child tweens play by moving a shared playhead. This is why you can `pause()`, `reverse()`, `timeScale()`, or `scrollTrigger`-scrub an entire sequence as one unit. Build sequences with `tl.to().to().to()` (chained on the *timeline instance*, not on `gsap`).
- **The position parameter controls overlap/gaps.** The third argument to `.to()/.from()/.fromTo()` on a timeline places it in time: a number is an absolute second, `"+=1"` is one second after the end of the timeline (gap), `"-=0.5"` overlaps the previous tween by half a second, and a label string (`"sectionStart"`) anchors it to a named spot. This is the single most important tool for making sequences feel "choreographed" instead of "things happening one after another."
- **Default ease is `power1.out`, default duration is `0.5s`.** Both are usually too subtle/fast for hero moments — landing pages typically want `power3`/`power4` outs for entrances and longer durations (0.6–1.2s) for anything the user is meant to *notice*.
- **`stagger` turns one tween into a cascade.** `stagger: 0.1` offsets each target's start time by 0.1s; `stagger: { amount: 0.5, from: 'start'|'center'|'edges'|'random'|[x,y] }` distributes a *total* duration across all targets regardless of count — `amount` is usually the better choice because it stays consistent whether you have 3 cards or 30.
- **`gsap.context()` is the cleanup primitive.** Wrap a block of animation-creation code in `gsap.context(() => {...}, scopeEl)` and later call `ctx.revert()` to kill/restore everything created inside it in one shot — essential for SPA route changes or any "rebuild this section's animations" flow (React's `useGSAP()` wraps this for you).

## Common gotchas
- **`immediateRender` defaults differ by method**: `to()` tweens default to `false` (nothing renders until the tween actually starts, so `gsap.set()` + `to()` won't fight), but `from()`, `fromTo()`, and anything with a `scrollTrigger` default to `true` — they render immediately on creation. If you build a `from()` tween that should wait, set `immediateRender: false` explicitly or you'll see a flash of the "from" state before anything triggers it.
- **`overwrite` is `false` by default**, meaning two tweens animating the same property of the same target will fight/jitter rather than one cancelling the other. If you're re-triggering animations on the same element (hover in/out, repeated scroll triggers), set `overwrite: 'auto'` or `overwrite: true`.
- **`gsap.to()` creates a standalone tween; `tl.to()` adds to a timeline.** Mixing the two mental models is the #1 source of "why isn't my sequence in order" bugs — if you want things sequenced, everything needs to be added via the timeline's own `.to/.from/.fromTo`, not `gsap.to()` calls sprinkled around.
- **Relative values need the `+=`/`-=` string prefix**, not raw arithmetic: `{x: "+=100"}` nudges by 100px from wherever the value currently is; `{x: 100}` sets an absolute destination. Forgetting the quotes/prefix silently does the wrong thing.
- **`yoyo` needs `repeat` to do anything** — `yoyo: true` with the default `repeat: 0` just plays once forward (yoyo only kicks in on repeat iterations). Use `repeat: -1, yoyo: true` for an infinite back-and-forth.
- **Function-based values are evaluated once per target on first render**, not continuously — `y: () => Math.random() * 100` gives each target a different (but fixed) value; it does not re-randomize every frame. Use `repeatRefresh: true` if you want fresh values on each repeat cycle.
- **`lazy` rendering (default `true`) can make `gsap.set()` immediately followed by reading a DOM property feel "stale"** for one tick — it batches writes to avoid layout thrashing. Rarely an issue, but worth knowing if a measurement right after a `set()` looks wrong.

## Recipes

**Hero entrance timeline (sequenced + overlapping, transform/opacity only):**
```js
const tl = gsap.timeline({ defaults: { ease: 'power3.out', duration: 0.8 } });
tl.from('.hero-title',    { opacity: 0, y: 40 })
  .from('.hero-subtitle', { opacity: 0, y: 30 }, '-=0.5')   // overlaps by 0.5s
  .from('.hero-cta',      { opacity: 0, y: 20, scale: 0.95 }, '-=0.4');
```

**Staggered card grid reveal with `amount` (consistent total duration regardless of card count):**
```js
gsap.from('.card', {
  opacity: 0, y: 50, scale: 0.96,
  duration: 0.7, ease: 'power3.out',
  stagger: { amount: 0.6, from: 'start' }
});
```

**Labeled timeline for a multi-stage logo/intro sequence (lets you seek/scrub to named beats):**
```js
const tl = gsap.timeline();
tl.addLabel('enter')
  .from('.logo', { opacity: 0, scale: 0.8, duration: 0.6, ease: 'back.out(1.7)' }, 'enter')
  .addLabel('settle', '+=0.2')
  .to('.logo', { y: -10, duration: 0.4, ease: 'power2.inOut' }, 'settle')
  .addLabel('reveal')
  .from('.tagline', { opacity: 0, y: 20, duration: 0.5 }, 'reveal');
```

## When to skip it
For a *single* property change with no relationship to other animations, a plain `gsap.to()`/`.from()` is already the simplest tool — don't wrap it in a timeline "just in case." And if the motion should be driven by scroll position rather than time, reach for `ScrollTrigger` (often paired with a timeline) rather than trying to fake scroll-linkage with `onUpdate` callbacks and manual scroll listeners.
