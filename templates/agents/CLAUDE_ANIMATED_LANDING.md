# Animated Landing Page Agent — kapitein-cdk

You are building an animated landing page using the kapitein-cdk serverless stack.
Use GSAP for all animations. Make the page feel modern, smooth, and polished.

## Your job

Build a single-page landing site in `src/frontend/`. No frameworks, no build step — just HTML, CSS, and JavaScript loaded from CDN. When finished, remind the user to push to the `main` branch to deploy.

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
- `src/frontend/css/style.css` — styles
- `src/frontend/js/main.js` — GSAP animations and any interactivity
- Images: `src/frontend/images/`

### GSAP (always include these for a landing page)

```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/ScrollTrigger.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/SplitText.min.js"></script>
```

Register plugins before use:
```js
gsap.registerPlugin(ScrollTrigger, SplitText);
```

### Animation patterns to use

**Hero entrance** — text splits and rises, background fades in:
```js
const heroTitle = new SplitText(".hero-title", { type: "lines,words" });
gsap.from(heroTitle.words, {
  opacity: 0, y: 80, duration: 0.9, stagger: 0.05, ease: "power3.out"
});
gsap.from(".hero-subtitle", { opacity: 0, y: 30, duration: 0.8, delay: 0.4 });
gsap.from(".hero-cta", { opacity: 0, y: 20, duration: 0.6, delay: 0.8 });
```

**Scroll reveals** — elements animate in as user scrolls:
```js
gsap.utils.toArray(".reveal").forEach(el => {
  gsap.from(el, {
    opacity: 0, y: 50, duration: 0.8,
    scrollTrigger: { trigger: el, start: "top 85%", toggleActions: "play none none none" }
  });
});
```

**Staggered cards**:
```js
gsap.from(".feature-card", {
  opacity: 0, y: 40, stagger: 0.12, duration: 0.7,
  scrollTrigger: { trigger: ".features", start: "top 75%" }
});
```

**Sticky header transition** — changes style on scroll:
```js
ScrollTrigger.create({
  start: "top -80",
  onUpdate: (self) => {
    document.querySelector("header").classList.toggle("scrolled", self.progress > 0);
  }
});
```

### API (only if the page has a form)

Load the API URL from the injected config:
```js
fetch("/config.json")
  .then(r => r.json())
  .then(config => { window.API_BASE_URL = config.apiUrl; });
```

The contact form handler is already deployed — POST to `window.API_BASE_URL + "/contact"` with `{ name, email, message }`.

### CORS
API Gateway allows all origins. Do not add CORS headers in Lambda.

### Deploying
User pushes to `main`. GitHub Actions deploys automatically. No local tools needed.

---

## Design principles for this agent

- **Performance first**: lazy-load images, keep animations at 60fps (use `transform` and `opacity` only)
- **Respect motion preferences**: wrap animations in `if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches)`
- **One strong CTA**: every section points toward the single action the user identified
- **Mobile-first CSS**: design for 375px width, then scale up with `min-width` media queries
- **Smooth scroll**: add `html { scroll-behavior: smooth; }` and anchor links for sections
