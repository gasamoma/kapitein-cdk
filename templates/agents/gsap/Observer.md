# Observer

## What it's for
Reach for Observer when you need to react to "scroll-like" user intent (wheel spin, touch swipe, pointer drag, scrollbar drag) in a unified way *without* hooking it to the actual page scroll position — custom horizontal-scroll sections, swipe-driven slide decks, drag-to-navigate galleries, "next/previous on swipe" interactions. If you instead want to trigger animations based on where the page *has scrolled to*, that's ScrollTrigger's job, not Observer's.

## Setup
```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/Observer.min.js"></script>
<script>
  gsap.registerPlugin(Observer);
</script>
```
**Important: if ScrollTrigger is already loaded, you do NOT need to load Observer separately.** ScrollTrigger bundles Observer internally (its `normalizeScroll()` is built on it) and exposes `ScrollTrigger.observe({...})`, which is functionally identical to `Observer.create({...})`. Loading both is redundant — pick one based on whether ScrollTrigger is already on the page.

## Key concepts
- **It normalizes wheel, touch, pointer, and scroll events into one callback API.** Instead of writing separate handlers for `wheel`, `touchmove`, `pointermove`, and `scroll` (and worrying about TouchEvent vs PointerEvent vs MouseEvent across browsers), you declare `type: "wheel,touch,pointer"` and get unified directional callbacks: `onUp`, `onDown`, `onLeft`, `onRight`, `onChange`, `onDrag`, `onHover`, `onClick`, etc.
- **Each tick's deltas are debounced and summed by default**, then the single largest delta determines which directional callback fires — this is what makes it feel smooth and intentional rather than jittery, and it's also a meaningful perf win (set `debounce: false` only if you specifically need per-event granularity).
- **Direction callbacks are about delta sign, not absolute position.** `onDown` fires when the *delta increases* (dragging down/swiping up triggers it — same convention as native scroll delta), `onUp` for the reverse. `wheelSpeed: -1` / `scrollSpeed: -1` are multipliers you can use to invert that mapping if it feels backwards for your interaction.
- **`onChange`/`onChangeX`/`onChangeY` keep firing throughout continuous movement** (subject to the `tolerance` threshold), whereas `onUp`/`onDown`/`onLeft`/`onRight` fire once per directional "event" — choose based on whether you want continuous tracking (e.g., dragging a slider) or discrete triggers (e.g., advancing to the next slide).
- **Every callback receives the Observer instance itself**, giving you `self.velocityX/Y`, `self.deltaX/Y`, `self.x/y`, `self.isDragging`, `self.event`, etc. — there's no need to track this state yourself.
- **`lockAxis: true` solves the classic "diagonal swipe picks the wrong direction" problem** — it locks the interaction to whichever axis the user moved first on, until they release, so a slightly-diagonal horizontal swipe doesn't also trigger vertical callbacks.

## Common gotchas
- **`tolerance` and `dragMinimum` exist to filter out noise — tune them for touch.** A finger resting on a phone screen registers a few pixels of "movement" even when the user thinks they're still; without a sensible `dragMinimum`/`tolerance`, you'll get false-positive triggers. Defaults are conservative but test on real touch devices.
- **`debounce: true` (default) means callbacks fire on the next `requestAnimationFrame` tick, not synchronously on the raw event** — if you need to call `event.preventDefault()` to stop native scrolling/zooming, make sure you're doing it from a path that still has access to the original event (`self.event`), and be aware the timing is one frame removed from the raw browser event.
- **`onMove` changes Observer's behavior** — defining it causes Observer to start measuring deltas continuously while merely *hovering* (not just pressing+dragging), which triggers `onUp`/`onDown`/`onChange` etc. for hover movement too. Only define `onMove` if you actually want that broader trigger surface; use `onDrag` if you specifically want press-and-drag-only.
- **`type` defaults to `"wheel,touch,pointer"` — NOT `"scroll"`.** If your interaction needs to react to actual `scroll` events (e.g., on an internally-scrolling container), you must explicitly add `"scroll"` to the `type` string — it's not included by default.
- **Don't double-load it.** If `ScrollTrigger` is present, loading `Observer.min.js` too just adds dead weight — use `ScrollTrigger.observe()` (identical API) instead.
- **`kill()` is permanent; `disable()` is not.** If you'll need to re-enable the same Observer later (e.g., toggling a horizontal-scroll mode on/off based on viewport width via `matchMedia`), use `disable()`/`enable()` — `kill()` removes it from the internal registry entirely and makes it ineligible for reuse.

## Recipes

**Swipe/wheel-driven "next/previous" section navigation (no native scrolling involved):**
```js
let busy = false;
Observer.create({
  type: 'wheel,touch,pointer',
  wheelSpeed: -1,           // normalize wheel direction to match swipe direction
  onDown: () => !busy && goToSection(currentIndex - 1),
  onUp:   () => !busy && goToSection(currentIndex + 1),
  tolerance: 10,
  preventDefault: true
});

function goToSection(index) {
  busy = true;
  gsap.to('.sections-track', {
    yPercent: -100 * index, duration: 0.8, ease: 'power3.inOut',
    onComplete: () => (busy = false)
  });
  currentIndex = index;
}
```

**Horizontal drag-to-scroll showcase strip (transform-only, follows pointer 1:1 while dragging):**
```js
const track = document.querySelector('.showcase-track');
let x = 0;
Observer.create({
  target: track,
  type: 'pointer,touch',
  onDrag: (self) => {
    x += self.deltaX;
    x = gsap.utils.clamp(-maxScroll, 0, x);
    gsap.set(track, { x });
  },
  onDragEnd: (self) => {
    // let it coast a bit based on release velocity (transform-only)
    gsap.to(track, { x: gsap.utils.clamp(-maxScroll, 0, x + self.velocityX * 0.2), duration: 0.6, ease: 'power3.out' });
  }
});
```

**Hover-driven micro-interaction on a card (direction-aware tilt):**
```js
Observer.create({
  target: '.tilt-card',
  type: 'pointer',
  onMove: (self) => {
    gsap.to('.tilt-card', { rotateY: self.x * 0.02, rotateX: -self.y * 0.02, duration: 0.4, ease: 'power2.out' });
  },
  onHoverEnd: () => gsap.to('.tilt-card', { rotateX: 0, rotateY: 0, duration: 0.5, ease: 'power3.out' })
});
```

## When to skip it
If you only need to know *when an element scrolls into view* (not raw gesture/velocity data), ScrollTrigger alone is simpler and more purpose-built. And if ScrollTrigger is already loaded on the page, never load `Observer.min.js` separately — call `ScrollTrigger.observe({...})` instead, which is the exact same API bundled in. For drag interactions that need realistic momentum/inertia after release (carousels that "coast"), pair Observer's drag data with **InertiaPlugin** or reach for **Draggable** (which has inertia integration built in) rather than hand-rolling velocity-based easing.
