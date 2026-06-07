# Flip

## What it's for
Reach for Flip when an element (or group of elements) needs to smoothly animate between two completely different DOM/CSS states — a different layout position, size, parent container, or even a swap with another element — instead of a simple property tween. It's the right tool whenever the "before" and "after" would otherwise cause a visual jump (filter grids re-sorting, cards expanding into modals, nav items relocating, logo letters flying from a splash screen into the header).

## Setup
```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/Flip.min.js"></script>
<script>
  gsap.registerPlugin(Flip);
</script>
```
Flip has no required dependencies, but it returns a GSAP timeline, so any other plugin/ease you already use (CustomEase, etc.) composes naturally with it. It pairs especially well with ScrollTrigger (flip a layout when a section comes into view) and with class-toggling UI code you already have.

## Key concepts
- **FLIP = First, Last, Invert, Play.** You capture the *current* ("First") layout state, mutate the DOM/CSS into the *end* ("Last") state, and Flip immediately snaps everything back to where it was (the "Invert") and then animates the offsets away ("Play") — so it *looks* like a single continuous motion even though the DOM changed in between.
- **The three-step rhythm is always the same**: `Flip.getState(targets)` → make your real DOM/class/style changes → `Flip.from(state, {...})`. Nothing in between needs to go through the plugin.
- **`data-flip-id` correlates elements across states.** Flip auto-assigns `auto-1`, `auto-2`, etc. if you don't set one, but to flip *between two different elements* (e.g., a thumbnail morphing into a hero image, or splash-logo letters landing on nav-logo letters) both elements must share the same `data-flip-id` so Flip knows they're "the same thing."
- **`Flip.from()` returns a timeline**, not a plain tween — you can `add()` other animations to it, control playback, or let it get force-completed if interrupted.
- **`absolute: true` takes the element out of document flow during the flip.** This is the standard fix for flex/grid layouts where elements would otherwise fight the layout engine mid-animation — but remember it can collapse surrounding space, so scope it to a subset (`absolute: ".card"`) rather than the whole layout when needed.
- **Nested transforms, rotation, and scale are all handled correctly** — Flip calculates real on-screen position/size even through scaled/rotated parent containers (most naive FLIP implementations break here). The one thing it does *not* handle is 3D transforms (`rotationX`, `rotationY`, `z`).

## Common gotchas
- **`Flip.getState()` must run BEFORE the DOM mutation, full stop.** If you call it after toggling the class/moving the element, you've captured the "Last" state as "First" and there's nothing to animate from. This sounds obvious but is the #1 mistake — especially in event handlers where async code runs the mutation first.
- **In frameworks (React/Vue/Angular), the re-render often replaces the DOM nodes Flip captured.** `Flip.getState()` remembers specific *element instances* plus their `data-flip-id`. If the framework re-renders new instances, `Flip.from(state)` with no `targets` won't find a match and silently does nothing. Always pass `targets: ".your-class"` explicitly so Flip re-queries the live DOM and matches by `data-flip-id`:
  ```js
  // BAD — may silently no-op after a re-render
  Flip.from(state, { duration: 1 });
  // GOOD — re-queries the DOM and matches by data-flip-id
  Flip.from(state, { targets: ".your-class", duration: 1 });
  ```
- **Frameworks don't render synchronously.** Calling `Flip.from()` immediately after triggering a state change can capture/animate against stale layout. Wait a tick — `requestAnimationFrame(() => Flip.from(...))` or a `useLayoutEffect` — or use `Flip.batch()` so the sequencing is handled for you.
- **`onLeave` elements are invisible unless `absolute: true` is also set** — Flip won't show a "leaving" element mid-animation if it's still in normal document flow (it'd throw off layout), so you must combine `onLeave` with `absolute: true` (Flip then temporarily restores its previous `display` value for the duration of the flip).
- **Set transform-related values through GSAP, not raw CSS**, whenever the element might also be Flipped — GSAP caches transform data for performance/accuracy, and stale CSS-only changes can throw off Flip's calculations. If you must reset, use `gsap.set(el, { clearProps: "transform" })`.
- **Use `box-sizing: border-box`** on flippable elements — Flip's width/height math assumes it, and `content-box` elements can produce subtly-wrong size calculations.
- **Multiple independent Flips that run in the same tick can corrupt each other's measurements** (each `getState()` needs to run before any of them mutate the DOM). Use `Flip.batch()` to coordinate them properly rather than calling `getState`/`from` in a loop.

## Recipes

**The core idiom — getState → mutate → from (e.g., splash-logo letters flying into the nav logo):**
```js
// 1. Capture where the letters are RIGHT NOW (on the splash screen)
const state = Flip.getState(".logo-letter", { props: "opacity" });

// 2. Make the real DOM change — move/re-parent the letters into the nav logo slot
//    (e.g., append them into the nav element, toggle classes, whatever the end state needs)
navLogo.append(...logoLetters);
splashScreen.classList.add("is-hidden");

// 3. Animate FROM the captured (splash) position TO the new (nav) position
Flip.from(state, {
  targets: ".logo-letter",     // re-query in case nodes were re-created
  duration: 1.1,
  ease: "power3.inOut",
  absolute: true,              // keep letters out of flow mid-flight so layout doesn't jump
  stagger: 0.04,
  onComplete: () => splashScreen.remove()
});
```

**Filter/sort grid reflow (cards rearranging without a jump):**
```js
function applyFilter(category) {
  const state = Flip.getState(".card");
  cards.forEach(card => card.classList.toggle("is-hidden", !matches(card, category)));
  Flip.from(state, {
    duration: 0.6,
    ease: "power2.out",
    absolute: true,
    stagger: 0.03,
    onEnter: els => gsap.fromTo(els, { opacity: 0, scale: 0.8 }, { opacity: 1, scale: 1, duration: 0.4 }),
    onLeave: els => gsap.to(els, { opacity: 0, scale: 0.8, duration: 0.3 })
  });
}
```

**Card → modal expansion (element grows and relocates to fill the viewport):**
```js
function expandCard(card) {
  const state = Flip.getState(card, { props: "borderRadius" });
  card.classList.add("is-expanded");        // CSS makes it position:fixed, full-bleed
  Flip.from(state, {
    duration: 0.5,
    ease: "power2.inOut",
    absolute: true,
    scale: true                              // scale instead of animating width/height (better perf)
  });
}
```

## When to skip it
If you're just animating an element's own properties (fade in, slide up, scale on hover), `gsap.to`/`gsap.from`/timelines are simpler and faster — Flip is overkill for anything that doesn't involve a genuine before/after *layout* change. Likewise, if you only need to morph one SVG shape into another (not reposition/resize a DOM element), reach for MorphSVGPlugin instead.
