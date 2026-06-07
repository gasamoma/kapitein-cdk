# ScrambleTextPlugin

## What it's for

Reach for ScrambleText when you want text to feel like it's being "decoded" — random characters cycle in place before resolving into the final string. It's the plugin behind hacker/terminal aesthetics, tech-brand stat reveals, and rollover effects. Don't use it for ordinary headline reveals (that's SplitText's job) — ScrambleText is specifically for the "scrambling → resolving" visual, not for splitting/staggering text into pieces.

## Setup

```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/ScrambleTextPlugin.min.js"></script>
<script>
  gsap.registerPlugin(ScrambleTextPlugin);
</script>
```

No dependencies on other plugins. It pairs naturally with `ScrollTrigger` (trigger the scramble when a stat or headline scrolls into view) and sits well alongside `SplitText` if you want to scramble individual words/chars rather than a whole block.

## Key concepts

- **It's a tween property, not a standalone API.** You don't call `ScrambleTextPlugin.something()` — you animate the `scrambleText` special property via `gsap.to()`/`gsap.from()` on an element, and the plugin rewrites that element's text content over the tween's duration.
- **The tween's `duration` controls the whole effect's length** — scrambling, the gradual reveal, everything happens within that window. There's no separate "how long to scramble" knob outside of `revealDelay`.
- **`{original}` (or simply omitting `text`) replays the element's existing text** — useful when you want to scramble-in the text that's already in the DOM (e.g. a stat that's server-rendered) rather than typing it out again in JS.
- **Reveal direction and granularity are configurable**: `delimiter` controls whether characters resolve one-by-one (default `""`) or word-by-word (`" "`), and `rightToLeft: true` reverses the resolve direction.
- **`chars` defines the "noise" alphabet** — `"upperCase"`, `"lowerCase"`, `"upperAndLowerCase"`, or any custom string like `"01"` for a binary look or `"!@#$%"` for glitch noise. This is the single biggest lever for matching the effect to your brand's vibe.

## Common gotchas

- **Scrambled noise characters do NOT inherit any styling distinction from the final text by default.** If you want the "in-flux" characters to look different (different color, weight, etc.) from the settled text, you must set `oldClass`/`newClass` — the plugin wraps old/new spans in those classes for you, but you still write the CSS.
- **Length mismatches cause a visible jump unless you account for `tweenLength`.** It defaults to `true` (the element gradually grows/shrinks to the new length), which is usually what you want for natural-looking layout — but combined with the "animate only transform/opacity" rule, a growing/shrinking text node can shift surrounding layout. Give the container a fixed width or `min-width` so the reflow doesn't cascade into neighboring elements.
- **`speed` is a refresh-rate multiplier, not a duration** — it controls how often the random characters are re-rolled (default `1`), independent of the tween's `duration`. Slowing it down (e.g. `0.2`) makes the scramble feel more deliberate/glitchy without changing how long the whole reveal takes.
- **Numeric content needs `chars: "0123456789"`** (or similar) — using the default `"upperCase"` on a number/stat looks wrong (letters flashing where digits should be). This is the most common mismatch when adapting a text demo to a stats counter.
- **Restarting/rewinding reverts the text**, just like TextPlugin — if your trigger can fire more than once (e.g. a `ScrollTrigger` without `once: true`), the element will scramble back to its original text on reverse, which may or may not be the effect you want.

## Recipes

**Stat counter that "decodes" into view on scroll:**
```js
document.querySelectorAll('.stat-number').forEach(el => {
  gsap.to(el, {
    duration: 1.5,
    scrambleText: {
      text: '{original}',       // re-reveal the value already in the markup
      chars: '0123456789',
      revealDelay: 0.3,         // stay fully scrambled for the first 0.3s
      speed: 0.4
    },
    scrollTrigger: { trigger: '.stats', start: 'top 80%', once: true }
  });
});
```

**Hero headline "decoding in" on load (terminal aesthetic):**
```js
gsap.set('.hero-title', { opacity: 1 }); // text starts visible-but-scrambled, not hidden
gsap.from('.hero-title', {
  duration: 2,
  scrambleText: {
    text: '{original}',
    chars: 'upperAndLowerCase',
    revealDelay: 0.2,
    newClass: 'is-resolved',    // style settled text distinctly in CSS
    speed: 0.3
  },
  delay: 0.4
});
```

**Word-by-word reveal on a CTA label (subtler, less "glitchy"):**
```js
gsap.to('.cta-label', {
  duration: 1,
  scrambleText: { text: 'GET STARTED TODAY', chars: 'XO', delimiter: ' ' }
});
```

## When to skip it

If you just need text to fade/slide/stagger into view, use `SplitText` + `gsap.from()` — ScrambleText's visual is a specific "decoding" effect and looks out of place on warm/minimal/editorial designs. If you need a classic typewriter (characters appearing in sequence, no randomized noise), reach for `TextPlugin` instead — it's lighter conceptually and doesn't carry the "hacker" connotation.
