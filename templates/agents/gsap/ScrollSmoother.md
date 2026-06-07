# ScrollSmoother

## What it's for
Reach for ScrollSmoother when you want the whole page to feel "premium" — silky momentum scrolling plus easy declarative parallax (`data-speed`/`data-lag` attributes) — without the accessibility problems that plague most JS smooth-scroll libraries (it rides on the browser's *native* scrollbar rather than faking one). It's a page-level decision, not a per-section one: you wrap your entire content in the smoother's wrapper/content structure once.

## Setup
```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/ScrollTrigger.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/ScrollSmoother.min.js"></script>
<script>
  gsap.registerPlugin(ScrollTrigger, ScrollSmoother);
</script>
```
**Hard dependency: ScrollSmoother is built on top of ScrollTrigger** — always load and register both. Create the smoother **before** any `ScrollTrigger.create()` calls or `scrollTrigger:` configs in your tweens, since everything downstream measures against the smoothed structure.

Required HTML structure — content must be wrapped:
```html
<body>
  <div id="smooth-wrapper">
    <div id="smooth-content">
      <!-- ALL your page content goes here -->
    </div>
  </div>
  <!-- position: fixed elements (nav, modals) go OUTSIDE the wrapper -->
</body>
```
With those default IDs, `ScrollSmoother.create({...})` finds them automatically — no need to pass `wrapper`/`content`.

## Key concepts
- **It moves *content*, not the scrollbar.** The real scrollbar stays on `<body>` and reflects native scroll position; ScrollSmoother then applies a CSS transform (`matrix3d`) to the `#smooth-content` element to gradually "catch up" to that position over `smooth` seconds (default `0.8`). This native-scroll foundation is *why* it avoids the touch/accessibility quirks of fake-scrollbar libraries.
- **`data-speed` is declarative parallax — no JS needed per element.** `data-speed="0.5"` makes an element appear to scroll at half speed (drifts toward you), `data-speed="2"` at double speed (drifts away), `data-speed="auto"` calculates the maximum parallax range automatically based on how much larger the element is than its `overflow: hidden` parent. Just set `effects: true` on creation and ScrollSmoother scans the DOM for these attributes.
- **`data-lag` makes an element "lazily" trail the scroll** — `data-lag="0.5"` takes half a second to catch up to where it should be, producing a pleasing drift/stagger effect when applied with slightly different values to nearby elements.
- **Effects reach their "natural" position when centered in the viewport** — this is the baseline `data-speed` is measured against, which is why elements near the very top/bottom of the page can look initially offset from their authored position. Fix above-the-fold offset with `clamp()`: `data-speed="clamp(0.5)"`.
- **One instance per page.** `ScrollSmoother.create()` returns (and `.get()` retrieves) a singleton — you configure the whole-page scroll experience once, then use `.effects()` to add parallax/lag to additional targets dynamically afterward if needed.

## Common gotchas
- **`position: fixed` elements MUST live outside `#smooth-wrapper`.** Because the content element gets a CSS transform applied, the browser creates a new containing block — any `fixed` descendant becomes fixed *relative to the transformed content*, not the viewport, so it scrolls away instead of sticking. Move sticky navs/modals/cookie-banners outside the wrapper, or use ScrollTrigger's `pin` instead of CSS `fixed` for in-flow sticky elements.
- **Mobile/touch smoothing is OFF by default** (`smoothTouch: false`) because users find it disorienting when the scroll disconnects from their finger. Only enable it deliberately (`smoothTouch: 0.1` for a short catch-up) — and test on real devices, since community reports note mobile lag/performance issues are common with ScrollSmoother, especially on image-heavy pages.
- **`normalizeScroll` doesn't fully solve the iOS address-bar jump.** Even with it enabled (and `event.preventDefault()` called internally), recent iOS versions still show/hide the address bar, which can trigger a resize → `ScrollTrigger.refresh()` → visual jump. The documented workaround is `ScrollTrigger.config({ ignoreMobileResize: true })`.
- **Combining ScrollSmoother with ScrollTrigger `snap` can feel laggy** (community-reported) — snapping waits for the smoothed scroll to fully settle before animating to the target, so the "snap" can feel delayed compared to a non-smoothed page. If snap responsiveness is critical, test carefully and consider tuning `smooth` lower.
- **Heavy/many DOM elements (especially unsized images) hurt smoothness** — community reports point to image-heavy sections as the most common cause of jank. Always size your images (explicit `width`/`height` or aspect-ratio CSS) so layout doesn't shift and ScrollTrigger measurements stay accurate; call `ScrollTrigger.refresh()` after any dynamically-loaded content changes the page height.
- **Don't nest `effects`** — the docs explicitly warn that `data-speed`/`data-lag` effects should not be applied to elements nested inside other effect elements; the calculations assume a flat relationship to the scroll container.

## Recipes

**Minimal page-wide setup with parallax/lag scanning enabled:**
```js
ScrollSmoother.create({
  smooth: 1,          // seconds to "catch up" to native scroll position
  effects: true,      // auto-detect data-speed / data-lag attributes
  smoothTouch: false  // keep native feel on phones (the safe default)
});
```

**Hero background that drifts slower than content (pure CSS attribute, transform-only under the hood):**
```html
<section id="hero">
  <div class="hero-bg" data-speed="clamp(0.6)"></div>
  <h1 class="hero-title">Headline</h1>
</section>
```

**Programmatic parallax for dynamically-rendered cards (no markup changes needed):**
```js
const smoother = ScrollSmoother.get(); // grab the existing singleton instance
smoother.effects('.feature-card .card-icon', { speed: 'auto', lag: 0.15 });
```

**Smooth "scroll to section" using the smoother's own method (keeps it in sync with the smoothing):**
```js
document.querySelectorAll('a[href^="#"]').forEach((link) => {
  link.addEventListener('click', (e) => {
    e.preventDefault();
    ScrollSmoother.get().scrollTo(link.getAttribute('href'), true, 'top top');
  });
});
```

## When to skip it
If the page only needs occasional scroll-triggered reveals (no whole-page momentum-scroll feel), skip ScrollSmoother entirely and use plain **ScrollTrigger** — it's lighter, has no wrapper/content structural requirements, and avoids the `position: fixed` containing-block trap altogether. Also skip it if the page is heavy on iframes, embeds, or third-party widgets that assume normal document flow — the transformed-content model can interact unpredictably with them.
