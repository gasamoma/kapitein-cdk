# ScrollTrigger

## What it's for
Reach for ScrollTrigger any time an animation's *playback* should be driven by scroll position rather than by time alone — reveal-on-scroll, parallax, pinned sections, scroll-scrubbed sequences, sticky nav state. For a one-off "play this when it scrolls into view," it's still the right tool (just a lighter config); for anything richer, pair it with a Timeline.

## Setup
```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/ScrollTrigger.min.js"></script>
<script>
  gsap.registerPlugin(ScrollTrigger);
</script>
```
Pairs natively with **ScrollSmoother** (built on top of ScrollTrigger — register both, create the smoother *before* any ScrollTriggers) and **Observer** (its `.observe()` is literally `Observer.create()` re-exposed, so you don't need to load Observer separately if ScrollTrigger is already present).

## Key concepts
- **It's an attachment, not a separate animation system.** Most commonly you add a `scrollTrigger: {...}` config object directly into a tween or timeline's vars — ScrollTrigger then drives that animation's playhead (or toggles play/pause/etc.) based on scroll. You can also use `ScrollTrigger.create({...})` standalone with callbacks (`onEnter`, `onUpdate`, etc.) for purely scroll-reactive logic that has nothing to do with animating properties.
- **`start`/`end` are "trigger-position vs viewport-position" pairs**, written as `"<element-position> <viewport-position>"` — e.g. `start: "top 80%"` means "when the top of the trigger element reaches 80% down the viewport." `"top top"`, `"center center"`, and `"bottom top"` are the other common combinations. `end` accepts relative offsets like `"+=500"` (500px of additional scroll past the start).
- **`scrub` vs `toggleActions` are two different control modes — pick one.** `scrub: true` (or a number like `scrub: 1` for a "catch-up" delay in seconds) directly links the animation's playhead to the scrollbar — the animation *is* the scroll position. `toggleActions: "play pause resume reset"` instead tells a time-based animation when to play/pause/reverse/reset at the four toggle points (enter, leave, enter-back, leave-back). Don't mix them on the same tween.
- **`pin: true` sticks the trigger element in place while the ScrollTrigger is active**, and by default adds spacer padding (`pinSpacing`) so subsequent content doesn't jump. Because pinning changes document flow/height, **the order you create ScrollTriggers matters** — triggers created after a pinning one need that pin's added scroll distance to already be accounted for, which only happens if they're created later (top-to-bottom on the page).
- **`markers: true` is your best debugging friend during development** — it overlays start/end lines with colors so you can see exactly where triggers fire. Always strip it before shipping.
- **`ScrollTrigger.batch()` groups nearby elements' enter/leave events** so you can fire one staggered animation for everything that scrolls into view around the same time, rather than triggering each element's own ScrollTrigger independently (much better for grids of cards/items).

## Common gotchas
- **Starting values get cached at creation time.** If you create a ScrollTrigger-driven tween while the element is in some interim state (or before layout settles), that becomes its recorded "from" value — and later `gsap.to()`/`gsap.set()` calls on the same properties won't refresh it. Fix by using `.fromTo()` explicitly, setting `immediateRender: false`, or — best — wrapping everything in one Timeline with a single ScrollTrigger so values are recorded together.
- **Don't apply `scrub` ScrollTriggers to individual tweens nested inside a timeline** — the parent timeline's playhead already controls those children, and a scrubbed ScrollTrigger wants to control the *same* playhead via scroll position. You end up with two systems fighting. Put the ScrollTrigger on the *timeline*, not on its children.
- **Never animate the pinned element itself.** ScrollTrigger pre-calculates pin measurements for performance; animating `transform`/size on the pinned element throws those measurements off and causes jumpy/broken behavior. Animate elements *nested inside* the pinned container instead.
- **Hard-coded pixel values don't survive resize.** `end: "+=500"` is fixed at creation time; if your layout is responsive, use a function-based value instead — `end: () => "+=" + document.querySelector('.panel').offsetHeight` — so it's recalculated on every `refresh()` (which fires automatically on resize).
- **One tween targeting a `.class` selector animates ALL matches simultaneously**, not each-on-its-own-scroll-trigger. If you want each card/section to reveal independently as it enters the viewport, loop over the elements and create a ScrollTrigger per element (or use `.batch()`).
- **`will-change: transform` (or any transform/filter) on an ANCESTOR of a pinned element breaks `position: fixed` pinning** — the browser creates a new containing block and the pin starts misbehaving (jumping, sticking to the wrong parent). This is a CSS/browser quirk, not a ScrollTrigger bug; the escape hatch is `pinReparent: true`, but prefer fixing the CSS.
- **Production builds can silently stop working** if your bundler tree-shakes the plugin because it "looks unused" (no direct reference) — explicit `gsap.registerPlugin(ScrollTrigger)` at the top avoids this. (Less of a concern with plain `<script>` tags as this project uses, but still good practice.)
- **Old `ScrollTrigger.matchMedia()` is deprecated** — for responsive variations, prefer `gsap.matchMedia()` (core) which integrates with `gsap.context()` for clean teardown between breakpoints.
- The docs page still references ScrollSmoother integration as a "members-only benefit" — that's **outdated**; as of late 2024 all GSAP plugins (including the formerly-paid "Club GreenSock" set: ScrollTrigger, ScrollSmoother, SplitText, MorphSVG, DrawSVG, Inertia) are 100% free, including for commercial use.

## Recipes

**Section reveal on scroll (most common landing-page pattern):**
```js
gsap.from('.feature-card', {
  opacity: 0, y: 60, duration: 0.8, ease: 'power3.out', stagger: 0.12,
  scrollTrigger: { trigger: '.features-grid', start: 'top 85%' } // fires once by default unless re-entering
});
```

**Scrubbed parallax layer (smooth-linked to scroll, animate transform only):**
```js
gsap.to('.hero-orb', {
  yPercent: -30, ease: 'none',
  scrollTrigger: {
    trigger: '#hero', start: 'top top', end: 'bottom top',
    scrub: 1.2 // takes 1.2s to "catch up" — softer than scrub: true
  }
});
```

**Pinned storytelling section with a labeled, snap-to timeline:**
```js
const tl = gsap.timeline({
  scrollTrigger: {
    trigger: '.story', start: 'top top', end: '+=2000', pin: true, scrub: 1,
    snap: { snapTo: 'labels', duration: { min: 0.2, max: 0.6 }, ease: 'power1.inOut' }
  }
});
tl.addLabel('one').from('.story-step1', { opacity: 0, y: 40 })
  .addLabel('two').to('.story-step1', { opacity: 0, y: -40 })
  .from('.story-step2', { opacity: 0, y: 40 }, '<')
  .addLabel('three');
```

## When to skip it
For a single "fade this in once when it appears and never touch it again," `gsap.from()` plus a basic `scrollTrigger: '.selector'` shorthand is enough — don't reach for the full config object with callbacks/snap/pin if all you need is a one-shot reveal. And if all you actually want is silky momentum scrolling with built-in parallax (`data-speed`/`data-lag`), use **ScrollSmoother** — it's built on ScrollTrigger and handles the "smooth scroll feel" far better than hand-rolling it with scrub tweens.
