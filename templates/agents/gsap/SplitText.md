# SplitText

## What it's for
Reach for SplitText whenever a headline, subhead, or short paragraph needs to animate word-by-word, line-by-line, or character-by-character — hero title reveals, section-title wipes, dramatic pull-quotes. Don't use it for body copy or anything long; it creates one DOM element per chunk, which gets expensive fast.

## Setup
```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/SplitText.min.js"></script>
<script>
  gsap.registerPlugin(SplitText);
</script>
```
SplitText is one of the few GSAP plugins that can technically run *without* the core — but in this project's setup, always load core first and register normally. It commonly pairs with **ScrollTrigger** (trigger the reveal as the heading scrolls into view).

## Key concepts
- **As of v3.13 the API is `SplitText.create()`, not `new SplitText()`.** This was a major rewrite ("half the size, 14 new features") — `SplitText.create('.headline', { type: 'words, chars' })` returns an instance with `.chars`, `.words`, `.lines` arrays you feed straight into `gsap.from()`/`gsap.to()`.
- **`onSplit()` is the new recommended place to build your animation**, especially when combined with `autoSplit: true`. SplitText calls `onSplit(self)` every time it (re)splits — including the very first time — and if you `return` a tween/timeline from it, SplitText automatically reverts the old animation and time-syncs the new one whenever a re-split happens (font load, resize, etc.). This makes responsive line-splitting "just work":
  ```js
  SplitText.create('.headline', {
    type: 'lines', autoSplit: true,
    onSplit(self) {
      return gsap.from(self.lines, { opacity: 0, y: 60, stagger: 0.08, duration: 0.7, ease: 'power3.out' });
    }
  });
  ```
- **Accessibility is built in by default (`aria: 'auto'`).** SplitText automatically adds `aria-label` (populated from the original text) to the parent and `aria-hidden` to every generated chunk, so screen readers announce the real sentence instead of spelling out individual letters. You don't need to do anything extra for plain text — but if your heading contains links or `<strong>`/`<em>` tags whose semantics matter, switch to `aria: 'none'` and provide a visually-hidden duplicate instead (the default approach won't surface nested element semantics).
- **`mask: 'lines' | 'words' | 'chars'` gives you reveal-effect wrapping for free** — each chunk gets wrapped in an extra element with clipping applied, perfect for "text slides up from behind a mask" effects without writing your own wrapper markup.
- **`revert()` restores the original `innerHTML`.** Because splitting creates a lot of extra DOM nodes (expensive to keep around), call `split.revert()` in `onComplete` once the animation finishes — especially for one-shot hero reveals that never need to re-run.

## Common gotchas
- **Splitting before web fonts finish loading causes misaligned/shifted text** (SplitText will even `console.warn()` you about this). Either wrap your split call in `document.fonts.ready.then(() => {...})`, or set `autoSplit: true` so SplitText automatically reverts and re-splits once fonts are ready — but if you use `autoSplit`, you MUST build your animation inside `onSplit()`, not outside it, or your tween will reference stale (reverted) elements.
- **Splitting by `chars` alone produces ugly mid-word line breaks.** Always pair `chars` with `words` or `lines` in the `type` string (e.g. `type: "chars, words"`), or set `smartWrap: true`, so word groupings stay intact when text wraps.
- **Lines need re-splitting on resize — that's what `autoSplit` is for.** Unlike words/characters (which reflow naturally), each "line" element physically encloses a fixed set of words. Resize the container or load a different font and the *visual* lines no longer match the split DOM unless you revert-and-resplit. `autoSplit: true` handles this automatically (and also on font load).
- **Kerning shifts are a known visual artifact** — putting each character in its own element can subtly change letter spacing because the browser can no longer apply kerning pairs across element boundaries. Mitigate with `font-kerning: none; text-rendering: optimizeSpeed;` in CSS on the split element.
- **SEO risk on `<h1>` splits** — search engines may index the fragmented chunks rather than the full heading. Keep `aria: "auto"` (the default) enabled and make sure the page's `<title>`/meta description carry the real content, since a split heading might otherwise show up in results in pieces.
- **Only split what you actually animate.** Splitting into chars+words+lines for a long block of text can mean *thousands* of new DOM nodes — a real performance cost. If you only animate `.words`, set `type: "words"` and skip the rest.
- **`text-wrap: balance` interferes with clean splitting** — avoid combining the two.
- **Not for SVG `<text>`** — SplitText is designed for HTML text content only.

## Recipes

**Hero headline — word-by-word reveal with 3D tilt (transform/opacity only):**
```js
const heroSplit = SplitText.create('.hero-title', { type: 'words' });
gsap.set(heroSplit.words, { opacity: 0, y: 60, rotateX: -60, transformPerspective: 600, transformOrigin: 'center bottom' });
gsap.to(heroSplit.words, {
  opacity: 1, y: 0, rotateX: 0,
  stagger: { amount: 0.5 }, duration: 0.7, ease: 'power4.out',
  onComplete: () => heroSplit.revert() // clean up the extra DOM once it's done
});
```

**Section title — masked line wipe, triggered on scroll:**
```js
document.querySelectorAll('.section-title').forEach((el) => {
  SplitText.create(el, {
    type: 'lines', mask: 'lines',
    onSplit(self) {
      return gsap.from(self.lines, {
        yPercent: 110, duration: 0.9, ease: 'power3.out', stagger: 0.12,
        scrollTrigger: { trigger: el, start: 'top 88%' }
      });
    }
  });
});
```

**Responsive headline that survives resize/font-load (autoSplit):**
```js
SplitText.create('.responsive-headline', {
  type: 'words, lines',
  autoSplit: true, // re-splits on font load / width changes
  onSplit(self) {
    // ALWAYS build the animation in here when autoSplit is true
    return gsap.from(self.lines, { opacity: 0, y: 40, stagger: 0.1, duration: 0.6, ease: 'power3.out' });
  }
});
```

## When to skip it
For long-form body copy, just animate the whole block's opacity/transform — splitting hundreds of words into individual elements is a performance drag for very little visual payoff. And if all you want is a basic "fade and slide up" on a heading (no per-word/char choreography), skip SplitText entirely and animate the element itself with `gsap.from()` — simpler, faster, and one less plugin to load.
