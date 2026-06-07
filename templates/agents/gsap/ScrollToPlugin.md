# ScrollToPlugin

## What it's for
A small, focused plugin: it animates the *scroll position* of the window or a scrollable element to a target — smooth nav-anchor links, "back to top" buttons, "scroll to next section" arrows. It is purely about moving the scrollbar smoothly; it does not trigger or coordinate other animations based on scroll (that's ScrollTrigger's job).

## Setup
```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/ScrollToPlugin.min.js"></script>
<script>
  gsap.registerPlugin(ScrollToPlugin);
</script>
```
No other plugin dependencies. It's commonly used alongside **ScrollTrigger** on the same page (one drives scroll-position-based animation, the other animates *to* scroll positions on click) — but they don't depend on each other. If a **ScrollSmoother** is active on the page, prefer its own `.scrollTo()` method instead (see below) so the animated scroll stays in sync with the smoothing layer.

## Key concepts
- **It's a special property inside a normal tween — `scrollTo`, not a standalone API.** You animate `window` (for page scroll) or any element with `overflow: scroll`/`auto` (for an internal scroll container) by giving it a `scrollTo` value: `gsap.to(window, { duration: 1.5, scrollTo: 400 })`.
- **The target accepts numbers, selectors, or an `{x, y}` object.** A bare number/string is treated as the `y` position. `scrollTo: "#pricing"` scrolls the element with that ID into view; `scrollTo: { y: "#pricing", offsetY: 80 }` scrolls to it but stops 80px short — perfect for clearing a fixed nav bar.
- **`"max"` scrolls to the maximum possible position** — `scrollTo: { y: "max" }` or the shorthand `scrollTo: "max"` is the cleanest way to build a "scroll to bottom" / "scroll to end of content" action without measuring document height yourself.
- **`autoKill: true` hands control back to the user mid-animation.** If the user grabs the scrollbar or starts scrolling manually while the tween is running, `autoKill` detects that the position changed externally and cancels the remaining animation rather than fighting the user — generally what you want for any user-facing "scroll to" interaction. Pair with `onAutoKill` if you need to react to the cancellation.

## Common gotchas
- **Conflicts with CSS `scroll-behavior: smooth`.** The official docs explicitly warn that combining the two causes conflicts (the browser's native smooth-scroll fights GSAP's animated scroll). If you use ScrollToPlugin for anchor links, remove `scroll-behavior: smooth` from your CSS — don't use both.
- **Scrolling a `<div>` requires `overflow: scroll`/`auto` to already be set** — animating `scrollTo` on an element that doesn't actually scroll silently does nothing useful (there's no scroll position to change).
- **It only animates scroll position — it will NOT trigger ScrollTrigger-based reveals "early."** Because the scroll happens via a tween rather than user input, any `scrollTrigger`-driven animations along the way will still fire at the correct scroll positions (ScrollTrigger listens to the actual scroll position, not the input method) — but don't expect `ScrollToPlugin` itself to orchestrate anything beyond the scroll.
- **On a ScrollSmoother-enabled page, plain `gsap.to(window, {scrollTo: ...})` can fight the smoothing layer.** Use `ScrollSmoother.get().scrollTo(target, true, 'top top')` instead — it's aware of the smoothed content transform and won't produce a jarring desync.
- **Set a sensible `ease`.** The default `power1.out` is fine for short scrolls, but for long jumps (e.g., "back to top" from deep in the page) something like `power2.inOut` over a longer duration (1.2–2s) feels far less abrupt than a fast linear jump.

## Recipes

**Smooth nav-anchor links with offset for a fixed header (the project's standard nav pattern):**
```js
document.querySelectorAll('nav a[href^="#"]').forEach((link) => {
  link.addEventListener('click', (e) => {
    e.preventDefault();
    gsap.to(window, {
      duration: 1.2, ease: 'power2.inOut',
      scrollTo: { y: link.getAttribute('href'), offsetY: 70, autoKill: true }
    });
  });
});
```

**"Back to top" button:**
```js
document.querySelector('.back-to-top').addEventListener('click', () => {
  gsap.to(window, { duration: 1.5, ease: 'power2.inOut', scrollTo: { y: 0, autoKill: true } });
});
```

**"Scroll to next section" hero arrow (scroll exactly one viewport height):**
```js
document.querySelector('.scroll-cue').addEventListener('click', () => {
  gsap.to(window, {
    duration: 1, ease: 'power1.inOut',
    scrollTo: { y: window.innerHeight, autoKill: true }
  });
});
```

## When to skip it
If the page already uses **ScrollSmoother**, skip `gsap.to(window, {scrollTo})` for in-page navigation and call the smoother's own `.scrollTo()` method — it understands the smoothed content transform and won't desync. And if your only need is "jump instantly to an anchor with no animation," a plain `element.scrollIntoView()` (or even an `href="#id"` anchor link with `scroll-behavior: smooth` in CSS, *if* you're not also using ScrollToPlugin elsewhere) is simpler and needs no plugin at all.
