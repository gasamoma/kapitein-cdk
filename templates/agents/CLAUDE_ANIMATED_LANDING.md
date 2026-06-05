# Animated Landing Page Agent — kapitein-cdk

You are building an animated landing page using the kapitein-cdk serverless stack.
Use GSAP for all animations. Make the page feel modern, smooth, and polished.

## Your job

Build a single-page landing site in `src/frontend/`. No frameworks, no build step — just HTML, CSS, and JavaScript loaded from CDN. When finished, remind the user to push to the `main` branch to deploy.

---

## BEFORE WRITING ANY CODE — READ THE PAGE FIRST

If `src/frontend/index.html` already exists, **read it completely before making any changes.** Extract and reuse:
- Which GSAP plugins are already in `<script>` tags — do NOT add duplicates
- Which plugins are already in `gsap.registerPlugin(...)` — extend that call, don't replace it
- The existing CSS custom properties (`--accent`, `--surface`, etc.) — use them, don't invent new ones
- The existing class naming conventions — extend them consistently
- Any utility functions or animation patterns already defined in `<script>` — reuse them

**Never reinvent something that's already available on the page.** If SplitText is already loaded, use it. If a `startHero()` function exists, call it. If `--accent` is the brand color, use it.

This applies to edits AND new features. Always audit the existing page before writing a single line.

Ask the user:
1. What is this landing page for? (product, service, event, personal brand?)
2. What is the single most important action visitors should take? (sign up, book, buy, contact?)
3. How should it feel — bold and dramatic, clean and minimal, warm and personal, or something else?
4. What sections does it need? (suggest: Hero, Features/Benefits, Social proof, CTA, Footer)

After getting answers, build the full page without further questions.

---

## Stack

### File locations
- `src/frontend/index.html` — the entire page (one file is fine for a landing page)
- `src/frontend/css/style.css` — styles (or inline in `<style>`)
- `src/frontend/js/main.js` — GSAP animations and interactivity (or inline in `<script>`)
- Images: `src/frontend/images/`

---

## GSAP Plugin Reference

**ALWAYS use `gsap@3.15` — do not pick a different version number.**

All plugins below are available at `https://cdn.jsdelivr.net/npm/gsap@3.15/dist/<Plugin>.min.js` and are free to use.

Include only the plugins you actually need for the page. Register all of them together before any animation code runs.

### Plugin Dictionary

| Plugin file | What it does | Use it when |
|---|---|---|
| `gsap.min.js` | Core engine — tweens, timelines, all property animation | **Always. This is required.** |
| `ScrollTrigger.min.js` | Triggers animations on scroll position | Any scroll-based reveal, parallax, or pin |
| `SplitText.min.js` | Splits text into animatable words, chars, or lines | Hero headlines, word-by-word reveals, line wipes |
| `ScrollSmoother.min.js` | Smooth momentum scroll + built-in parallax (requires ScrollTrigger) | Premium feel — silky scroll with depth |
| `ScrollToPlugin.min.js` | Animates the viewport scrolling to a target | Smooth nav anchor links, "back to top" |
| `Observer.min.js` | Detects scroll/touch/pointer direction and velocity | Custom scroll behaviors, horizontal scroll sections |
| `Flip.min.js` | Smoothly animates elements between different DOM states/positions | Filter grids, tab switches, layout morphing |
| `Draggable.min.js` | Makes elements draggable with bounds and callbacks | Sliders, carousels, interactive drag UIs |
| `InertiaPlugin.min.js` | Momentum/throw physics after releasing a Draggable | Carousel that coasts after a flick |
| `ScrambleTextPlugin.min.js` | Text scrambles with random chars before settling on final text | Hacker/tech reveals, terminal aesthetic, stats counters |
| `TextPlugin.min.js` | Animates text content character by character | Typewriter effect |
| `DrawSVGPlugin.min.js` | Animates SVG stroke-dashoffset to "draw" paths | Drawing lines, signature animations, icon outlines appearing |
| `MorphSVGPlugin.min.js` | Smoothly morphs one SVG path shape into another | Logo transitions, icon state changes |
| `MotionPathPlugin.min.js` | Animates an element along an SVG `<path>` | Flying objects, orbits, curved entrances |
| `MotionPathHelper.min.js` | Dev overlay UI to edit motion paths visually | **Development only — remove before deploy** |
| `Physics2DPlugin.min.js` | Gravity, friction, acceleration on 2D position | Confetti, particle bursts, falling elements |
| `PhysicsPropsPlugin.min.js` | Physics forces on arbitrary CSS/SVG properties (not just x/y) | Custom physics simulations |
| `EasePack.min.js` | Adds `RoughEase`, `ExpoScaleEase`, `SlowMo` easing functions | Organic/rough movement, bouncy overshoots |
| `CustomEase.min.js` | Define any easing curve as an SVG cubic path string | Precise branded timing curves |
| `CustomBounce.min.js` | Custom bounce easing (requires CustomEase) | Cartoonish bouncy drops |
| `CustomWiggle.min.js` | Custom oscillation/wiggle easing (requires CustomEase) | Attention-grabbing jiggle effects |
| `GSDevTools.min.js` | Visual timeline debugger UI in the browser | **Development only — remove before deploy** |
| `EaselPlugin.min.js` | Integrates GSAP with CreateJS/EaselJS canvas API | Canvas/game projects using EaselJS only |
| `PixiPlugin.min.js` | Integrates GSAP with Pixi.js WebGL renderer | WebGL projects using Pixi.js only |

### How to include and register plugins

```html
<!-- Always include core first -->
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/gsap.min.js"></script>

<!-- Then add only the plugins you need, e.g.: -->
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/ScrollTrigger.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/SplitText.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/ScrambleTextPlugin.min.js"></script>

<!-- Register everything before writing any animation code -->
<script>
  gsap.registerPlugin(ScrollTrigger, SplitText, ScrambleTextPlugin);
  // All animation code goes here (DOM is ready since this script is at bottom of <body>)
</script>
```

**Important:** Always `registerPlugin()` before calling `new SplitText()`, `ScrollTrigger.create()`, etc. — even though GSAP auto-registers when loaded via `<script>`, explicit registration prevents tree-shaking issues and makes the code intention clear.

---

## Animation patterns

**Hero entrance — SplitText word reveal with stagger:**
```js
const heroTitle = new SplitText('.hero-title', { type: 'words' });
gsap.set(heroTitle.words, { opacity: 0, y: 60, rotateX: -60, transformPerspective: 600, transformOrigin: 'center bottom' });
// Then on DOMContentLoaded or immediately (script is at bottom of body):
gsap.to(heroTitle.words, {
  opacity: 1, y: 0, rotateX: 0,
  stagger: { amount: 0.5, from: 'start' },
  duration: 0.7, ease: 'power4.out'
});
gsap.to('.hero-subtitle', { opacity: 1, y: 0, duration: 0.7, delay: 0.4 });
gsap.to('.hero-cta',      { opacity: 1, y: 0, duration: 0.6, delay: 0.7 });
```

**Section title line reveal (SplitText lines):**
```js
document.querySelectorAll('.section-title').forEach(el => {
  const lines = new SplitText(el, { type: 'lines' });
  gsap.from(lines.lines, {
    opacity: 0, y: 50, stagger: 0.1, duration: 0.8, ease: 'power3.out',
    scrollTrigger: { trigger: el, start: 'top 88%' }
  });
});
```

**Scroll reveals — staggered cards:**
```js
gsap.from('.card', {
  opacity: 0, y: 60, scale: 0.95, stagger: 0.1, duration: 0.8, ease: 'power3.out',
  scrollTrigger: { trigger: '.cards-wrapper', start: 'top 85%' }
});
```

**Parallax orbs / background layers:**
```js
gsap.to('.orb', {
  y: -120, ease: 'none',
  scrollTrigger: { trigger: '#hero', start: 'top top', end: 'bottom top', scrub: 1.5 }
});
```

**ScrambleText stat counter reveal:**
```js
gsap.to('.stat-number', {
  duration: 1.5,
  scrambleText: { text: '{original}', chars: '0123456789', revealDelay: 0.3 },
  scrollTrigger: { trigger: '.stats', start: 'top 80%' }
});
```

**Sticky nav on scroll:**
```js
ScrollTrigger.create({
  start: 'top -60',
  onUpdate: self => {
    document.querySelector('nav').classList.toggle('scrolled', self.progress > 0);
  }
});
```

---

## API (only if the page has a form)

Load the API URL from the injected config:
```js
fetch('/config.json')
  .then(r => r.json())
  .then(config => { window.API_BASE_URL = config.apiUrl; });
```

POST to `window.API_BASE_URL` with `{ name, email, message, source }`.

### CORS
Lambda Function URL CORS is configured in the CDK stack. Do not add CORS headers manually in the handler.

### Deploying
User pushes to `main`. GitHub Actions deploys automatically. No local tools needed.

---

## Design principles

- **Performance**: animate only `transform` and `opacity` — never `width`, `height`, `top`, `left`
- **Respect motion**: wrap all animations in `if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches)`
- **Initial states via GSAP**: use `gsap.set()` to hide elements before animating them — never `opacity: 0` in CSS, because if JS fails the content stays visible
- **One strong CTA**: every section flows toward the single action the user identified
- **Mobile-first CSS**: design for 375px, then `min-width` media queries up
- **Smooth scroll**: `html { scroll-behavior: smooth; }` + anchor links for all sections
