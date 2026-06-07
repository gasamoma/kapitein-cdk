# CustomWiggle

## What it's for
Reach for CustomWiggle when you want an element to oscillate back and forth — a shake, jiggle, or wobble — for attention-grabbing micro-interactions (hover nudges, "look here" cues, playful logo treatments, error shakes). It's a thin wrapper that generates a `CustomEase` curve which oscillates a configurable number of times, so a single tween (e.g. `rotation: 30`) produces a natural-looking back-and-forth wiggle instead of a one-way move.

## Setup
```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/CustomEase.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/CustomWiggle.min.js"></script>
<script>
  gsap.registerPlugin(CustomEase, CustomWiggle);
</script>
```
**CustomWiggle extends CustomEase and requires it to be loaded and registered first** — both the `<script>` tag and the `registerPlugin()` call. Loading `CustomWiggle.min.js` alone is not enough.

## Key concepts
- **A wiggle is just an ease — the oscillation comes from the curve, not from special tween logic.** `CustomWiggle.create("myWiggle", { wiggles: 6 })` registers an ease ID; you then use it in a perfectly normal `gsap.to()` like `ease: "myWiggle"`. The ease curve itself moves the value up, down, up, down... back to its target.
- **The tween's *target value* controls the wiggle's amplitude/strength — not the ease config.** `rotation: 30` with `ease: "myWiggle"` wiggles harder than `rotation: 10` with the same ease. Think of the ease as "the rhythm" and the property delta as "the size of each swing."
- **`type` is a preset combination of two underlying controls:** `amplitudeEase` (how the *strength* of the oscillation changes over the tween — e.g. fading out toward the end) and `timingEase` (how the oscillations are *spaced* over time — e.g. front-loaded vs. evenly spread). The five `type` presets (`"easeOut"` default, `"easeInOut"`, `"anticipate"`, `"uniform"`, `"random"`) are convenient shortcuts for common amplitude/timing combos.
- **Defining `amplitudeEase` or `timingEase` explicitly overrides `type` entirely** — they're the "advanced" knobs underneath the presets, for when none of the five canned types feels right.
- **A wiggle naturally returns to its starting value** — `gsap.to(el, { rotation: 30, ease: "myWiggle" })` ends back at the element's original rotation, having swung through `+30`/`-30`-ish territory along the way (the exact swing pattern depends on `type`). This makes wiggles ideal for "nudge and return" interactions without needing a `yoyo` or a second tween.

## Common gotchas
- **`wiggles` must be an integer and represents oscillation *count*, not duration or intensity** — more wiggles packed into the same `duration` means faster, tighter shaking; the same `wiggles` value spread over a longer `duration` reads as slower, looser shaking. Tune `wiggles` and `duration` together.
- **A high `wiggles` count with a short `duration` can blur into a vibration rather than a readable shake** — for a human-perceptible "no no no" head-shake feel, something like `wiggles: 4-6` over `0.5-0.8`s usually reads better than `wiggles: 15` over `0.3`s.
- **Wiggling isn't limited to `rotation`** — it works on any animatable numeric property, including `x`/`y` (for a literal shake/jitter) or even combined for a "swarm"/jitter effect. Just remember the *property delta* sets the strength: `x: 8` wiggles much more subtly than `x: 40`.
- **The condensed string syntax (`ease: "wiggle(15)"` or `ease: "wiggle({type: anticipate, wiggles: 8})"`) only works once CustomWiggle is loaded and registered** — same trap as CustomBounce's string syntax. If you see `"wiggle(...)"` silently doing nothing, check plugin registration order first.
- **Don't overuse it** — a wiggle is an *interrupt*; it draws the eye precisely because it differs from everything else's smooth, purposeful motion. Wiggling more than one or two elements on a page (or wiggling on every scroll-into-view) reads as glitchy/broken rather than charming.

## Recipes

**Hover nudge on a CTA button (subtle "tap me" cue, returns to rest):**
```js
CustomWiggle.create('ctaNudge', { wiggles: 4, type: 'easeOut' });

document.querySelector('.hero-cta').addEventListener('mouseenter', () => {
  gsap.to('.hero-cta', { rotation: 4, duration: 0.5, ease: 'ctaNudge' });
});
```

**Form validation "shake" on error (classic horizontal jitter):**
```js
CustomWiggle.create('errorShake', { wiggles: 6, type: 'easeInOut' });

function shakeField(el) {
  gsap.to(el, { x: 10, duration: 0.4, ease: 'errorShake', clearProps: 'x' });
}
```

**Playful logo wiggle on scroll into view (anticipation feel, draws the eye once):**
```js
CustomWiggle.create('logoWiggle', { wiggles: 8, type: 'anticipate' });

gsap.from('.logo-mark', {
  rotation: 20,
  duration: 1.1,
  ease: 'logoWiggle',
  scrollTrigger: { trigger: '.logo-mark', start: 'top 85%', once: true }
});
```

## When to skip it
For a single, simple shake, `gsap.to(el, { x: '+=10', duration: 0.08, repeat: 5, yoyo: true })` gets you a basic back-and-forth with zero extra script tags — perfectly fine for a one-off error shake. Reach for CustomWiggle when you want the oscillation to feel *natural* (decaying amplitude, organic spacing via `type`/`amplitudeEase`/`timingEase`) rather than mechanically repetitive, or when you'll reuse the same wiggle "personality" across multiple elements.
