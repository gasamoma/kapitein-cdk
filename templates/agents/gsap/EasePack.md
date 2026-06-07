# EasePack

## What it's for
Reach for EasePack when a built-in ease (`power2.out`, `back.in`, etc.) is too "clean" for the effect you want. It adds three specialty eases — `RoughEase` (jittery/organic motion), `SlowMo` (decelerate → linear → accelerate, like a camera move), and `ExpoScaleEase` (corrects the perceived speed-up/slow-down that happens when you tween `scale`). Use plain `gsap.to()` with a stock ease for normal reveals; reach for EasePack specifically when you need texture, a "hang in the middle" pacing, or silky scale animations.

## Setup
```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/EasePack.min.js"></script>
<script>
  gsap.registerPlugin(EasePack);
</script>
```
One file (`EasePack.min.js`) registers all three eases at once — there's no separate `RoughEase`/`SlowMo`/`ExpoScaleEase` script. No other plugin dependencies. These eases are referenced as **strings** in tweens (`ease: "rough({...})"`, `ease: "slow(...)"`, `ease: "expoScale(1, 2)"`) — you don't need to hold a reference to anything after registering.

## Key concepts
- **Three distinct tools, one file.** `RoughEase` = jagged/random motion, `SlowMo` = smooth deceleration-hold-acceleration pacing, `ExpoScaleEase` = a corrective curve specifically for `scale`/`scaleX`/`scaleY`. They solve different problems — don't reach for `rough` when you actually want `slow`.
- **Configured via a string syntax**, not an object passed to `ease`. Write `ease: "rough({strength: 2, points: 30})"` — the curly braces and the whole thing are inside one string. This is easy to fat-finger (missing `}` or quotes silently breaks the ease lookup and GSAP falls back to a default).
- **`RoughEase` plots a fixed number of random points** along a template ease (default template is `"none"`, i.e. linear) and connects them — it is *not* true randomness each frame; the jagged path is calculated once at creation, like a pre-baked waveform.
- **`SlowMo` has three params in order**: `linearRatio` (how much of the middle is steady-paced, default `0.7`), `power` (strength of the in/out eases, default `0.7`), and `yoyoMode` (boolean — makes a *second* tween's ease mirror the first so paired animations, e.g. position + opacity, stay in sync).
- **`ExpoScaleEase` needs the start and end scale values baked into the ease string itself** — `"expoScale(1, 2)"` for animating scale from 1 → 2. If your `from`/`to` scale values change, the ease string must change too, or the curve will be wrong (it's solving the math for that specific range).

## Common gotchas
- **`expoScale` values must be non-zero** — the underlying math can't handle `0`. Use a small value like `0.01` instead of `0`. Don't go *too* small either (e.g. `0.00000001`): the tween spends a disproportionate amount of its duration crawling through the tiny end of the exponential curve, looking like it "hangs" before suddenly catching up.
- **The `expoScale` start/end values must match your tween's actual scale range**, not just be placeholder numbers — `gsap.to(el, { scale: 2, ease: "expoScale(1, 2)" })` assumes the element starts at scale `1`. If it actually starts at `0.5`, the curve will be subtly wrong and the animation won't feel as smooth as advertised.
- **`RoughEase` with `randomize: true` (the default) produces a different-looking jitter than `randomize: false`** — the latter zig-zags evenly, which combined with `taper` gives a controlled "settling" wobble. If your rough animation looks chaotic when you wanted a controlled wobble, try `randomize: false` with a `taper`.
- **`taper` only tapers the *strength* of the roughness, not the underlying template motion** — the element still follows the `template` ease's overall arc; only the jitter amplitude shrinks toward the tapered end.
- **String-based ease config is invisible to typos at compile time.** `ease: "rought({strength: 2})"` (note the typo) won't throw — GSAP just won't find that ease and silently uses the default. If your "rough" animation looks suspiciously smooth, check the string for typos first.

## Recipes

**Organic, slightly chaotic entrance (rough opacity reveal):**
```js
gsap.from('.hero-eyebrow', {
  opacity: 0,
  duration: 1.2,
  ease: 'rough({ strength: 1.5, points: 24, taper: "out", randomize: true })'
});
```

**Cinematic "zoom in, hold, zoom past" hero text move (SlowMo with synced fade):**
```js
gsap.to('.hero-headline', {
  x: 600,
  duration: 3,
  ease: 'slow(0.6, 0.7, false)'
});
// fade companion tween stays perfectly in sync via yoyoMode:
gsap.from('.hero-headline', {
  opacity: 0,
  duration: 3,
  ease: 'slow(0.6, 0.7, true)'
});
```

**Silky logo/icon scale-in (ExpoScaleEase):**
```js
gsap.fromTo('.logo-mark',
  { scale: 0.4 },
  { scale: 1, duration: 0.9, ease: 'expoScale(0.4, 1, power1.out)' }
);
```

## When to skip it
For ordinary reveals, stick with GSAP's built-in eases (`power2.out`, `back.out(1.4)`, `expo.out`) — they cover 95% of landing-page needs and are far more predictable. Reach for `RoughEase` only when "organic imperfection" is the actual design goal (it can read as "broken" if used on polished UI chrome). Use `ExpoScaleEase` only on `scale`/`scaleX`/`scaleY` tweens — for position, rotation, or opacity it adds nothing over a normal ease.
