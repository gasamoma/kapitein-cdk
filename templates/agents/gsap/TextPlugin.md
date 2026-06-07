# TextPlugin

## What it's for

Reach for TextPlugin specifically for a **typewriter effect** — text content being replaced character-by-character (or word-by-word) over a tween, with the DOM element's actual `textContent` changing as it plays. It's the right tool when the *content itself* needs to visibly type/change, not when you want characters to fade/slide/stagger in (that's `SplitText` territory) or scramble into place (that's `ScrambleTextPlugin`).

## Setup

```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/TextPlugin.min.js"></script>
<script>
  gsap.registerPlugin(TextPlugin);
</script>
```

No dependencies on other plugins. Commonly paired with `ScrollTrigger` (start typing when scrolled into view) or sequenced inside a `gsap.timeline()` alongside other hero-entrance tweens.

## Key concepts

- **It rewrites the element's text over the tween's lifetime** — when the tween finishes, the DOM text has been fully replaced by the `text` value; rewinding/restarting the tween reverts it back to the original. This is genuine DOM mutation, not a visual trick — keep that in mind for SEO/accessibility (screen readers may announce changes).
- **Plain string vs. config object** — `text: "new text"` uses all the defaults. Anything beyond the basic replacement (delimiter, classes, speed, etc.) requires the **nested object syntax**: `text: { value: "...", delimiter: " ", ... }`. Mixing the two (special properties at the top level alongside a string `text`) silently does nothing for those properties.
- **`speed` replaces guesswork around `duration`.** Typing 10 characters over 2 seconds looks completely different from typing 500 over 2 seconds — `speed` (think "changes per unit of time", formula `0.05 / speed * text_changes`) lets the plugin compute an appropriate pace instead of you hand-tuning duration per string length.
- **`delimiter` is the word-vs-character switch** — default `""` types one character at a time; `" "` (space) types whole words at a time, which often reads as more natural/less robotic for longer sentences.
- **`type: "diff"` skips identical leading/trailing portions** — if your start and end strings share a long common prefix, the default behavior re-types that shared part from scratch (looking like a delay before anything "interesting" happens); `diff` mode jumps straight to the actual differences.

## Common gotchas

- **`ease: "none"` is what the official examples use, and for good reason** — character-by-character replacement is a discrete, stepped change, so easing curves (which imply smooth continuous motion) don't map onto it the way they do for `x`/`opacity`. Leaving the default ease can make the typing feel like it accelerates/decelerates oddly.
- **Layout shift as text grows/shrinks.** TextPlugin literally changes the rendered string length mid-animation — a short placeholder growing into a long sentence will reflow surrounding content. Use `padSpace: true` to pad the trailing gap with non-breaking spaces (prevents the element from visually collapsing as text shrinks), and give the container a fixed height/width so neighboring elements don't jump — this is the practical way to respect the "no layout property animation" rule when the *content* itself is what's changing size.
- **`newClass`/`oldClass` wrap text in elements, which can break inline layout assumptions** — they're great for visually differentiating "already typed" vs "currently changing" text, but test how the wrapping interacts with your line-height/wrapping, especially with `delimiter: " "` where whole words get wrapped.
- **Restarting reverts the text** — same caveat as ScrambleText: if the trigger can fire repeatedly (no `once: true` on a ScrollTrigger, or a hover that re-triggers), expect the text to revert to its original value on reverse, not just stop.
- **HTML is handled, but only simple nodes** — TextPlugin recognizes basic tags like `<br>` (since 3.0.4) and honors them, but don't expect it to gracefully type through arbitrary nested markup; keep the animated string close to plain text.

## Recipes

**Classic hero typewriter (word-by-word, feels less mechanical):**
```js
gsap.to('.hero-tagline', {
  duration: 2,
  text: { value: 'Ship faster. Ship smarter. Ship with confidence.', delimiter: ' ' },
  ease: 'none',
  delay: 0.6
});
```

**Terminal-style line that types in on scroll, with a class on the "live" portion:**
```js
gsap.to('.terminal-line', {
  scrollTrigger: { trigger: '.terminal-line', start: 'top 85%', once: true },
  duration: 1.5,
  text: {
    value: '$ npm install your-product --save',
    newClass: 'is-typing',
    padSpace: true
  },
  ease: 'none'
});
```

**Sequenced multi-line typing in a timeline (each line waits for the previous):**
```js
const tl = gsap.timeline({ defaults: { ease: 'none' } });
tl.to('.line-1', { duration: 1.2, text: 'Building the future of...' })
  .to('.line-2', { duration: 1, text: { value: 'one commit at a time.', delimiter: ' ' } }, '+=0.2');
```

## When to skip it

If you want characters/words/lines to *appear* (fade, slide, rotate in) without actually mutating the text content over time, use `SplitText` + `gsap.from()` — it's far more performant (animates `transform`/`opacity` on pre-split elements rather than rewriting `textContent` every tick) and doesn't fight with screen readers. If the goal is a "decoding/glitching" look rather than a clean typewriter, use `ScrambleTextPlugin` instead.
