# PixiPlugin

## What it's for
PixiPlugin is **only relevant if the page renders its visuals through [PixiJS](https://pixijs.com/)** (a WebGL/canvas 2D renderer) rather than the DOM — e.g. a generative-art piece, an interactive game-like hero, or a particle/shader showcase running on a `<canvas>`. It bridges GSAP to Pixi's display-object API so you can animate Pixi sprites/graphics with normal `gsap.to()` calls instead of wrestling with Pixi's nested sub-objects (`.position.x`, `.scale.y`, `.skew.x`) and radian-based rotation.

## Setup
```html
<!-- Pixi.js itself must be loaded first -->
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/PixiPlugin.min.js"></script>
<script>
  gsap.registerPlugin(PixiPlugin);

  // PixiPlugin needs a reference to the PIXI namespace to find its classes:
  PixiPlugin.registerPIXI(PIXI);
</script>
```
**Two registration steps, not one** — `gsap.registerPlugin(PixiPlugin)` (so GSAP knows about the plugin) AND `PixiPlugin.registerPIXI(PIXI)` (so the plugin can find PixiJS's internal classes like filters). Skipping the second call is the most common setup mistake; the plugin will load without error but several features (colors, filters) silently won't work. No other GSAP plugin dependencies.

## Key concepts
- **Animate Pixi display objects through a single `pixi: {...}` config object**, not by setting properties directly on the object or its sub-objects:
  ```js
  // tedious / error-prone without the plugin:
  gsap.to(sprite.scale, { x: 2, y: 1.5, duration: 1 });
  gsap.to(sprite, { rotation: (60 * Math.PI) / 180, duration: 1 }); // radians!

  // with the plugin — flat, in degrees:
  gsap.to(sprite, { pixi: { scaleX: 2, scaleY: 1.5, rotation: 60 }, duration: 1 });
  ```
- **Rotation is in degrees, not radians** — a deliberate ergonomics fix, since PixiJS itself uses radians internally. This is the opposite of what a Pixi developer would expect from the raw API, which is exactly why the plugin is worth using.
- **CSS-style color strings just work**: `"red"`, `"#F00"`, `"rgb(255,0,0)"`, `"hsl(0,100%,50%)"`, or Pixi's native `0xFF0000` hex-number format — including **relative HSL adjustments** like `"hsl(+=180, +=0%, +=0%)"` to shift hue while leaving saturation/lightness alone.
- **Special "convenience" properties auto-create and animate filters for you**: `saturation`, `brightness`, `contrast`, `hue`, and `colorize`/`colorizeAmount` all drive a `ColorMatrixFilter` under the hood; `blur`/`blurX`/`blurY` drive a `BlurFilter`. You never manually instantiate or attach these filters — the plugin handles it.
- **Directional rotation suffixes** (`"_cw"`, `"_ccw"`, `"_short"`) control *which way* a rotation travels — e.g. `rotation: "-170_short"` takes the 20° clockwise route instead of the 340° counter-clockwise route a plain numeric tween would take. (Added in GSAP 3.2 — a non-issue at the locked 3.15.)

## Common gotchas
- **Forgetting `PixiPlugin.registerPIXI(PIXI)`** is the #1 issue — without it, the plugin can't locate Pixi's filter classes, so `colorize`, `saturation`, `blur`, etc. silently fail to animate even though basic properties like `x`/`scaleX`/`rotation` work fine. Only needs to be called once, globally, after Pixi is loaded.
- **Properties must go inside the `pixi: {...}` object**, not at the top level of the tween vars — `gsap.to(sprite, { x: 100 })` animates the *DOM-style* `x` GSAP normally looks for (which Pixi sprites don't have in the expected shape), whereas `gsap.to(sprite, { pixi: { x: 100 } })` correctly reaches into Pixi's `position.x`.
- **This plugin animates canvas-rendered objects, not DOM elements** — none of it applies to, or interacts with, regular HTML/CSS elements on the page. If your landing page is standard HTML/CSS (the overwhelmingly common case), this plugin does nothing useful for you.
- **There's no fixed list of "supported" properties** — the plugin is a general-purpose ergonomics layer over whatever properties the registered PIXI object exposes, so the authoritative reference for exactly what you can animate is the PixiPlugin TypeScript declarations, not a docs table.

## Recipes
PixiPlugin recipes are inherently canvas/WebGL-specific and don't fit the "animate transform/opacity on DOM elements" model this template otherwise follows. If you're building a Pixi-based showcase piece, the patterns are:

```js
// Smooth scale + rotation on a sprite (degrees, flat config — no radian math):
gsap.to(sprite, { pixi: { scaleX: 1.4, scaleY: 1.4, rotation: 25 }, duration: 1.2, ease: 'power2.out' });

// Color sweep on a graphics object using CSS-style relative HSL:
gsap.to(graphics, { pixi: { fillColor: 'hsl(+=120, +=0%, +=0%)' }, duration: 2, ease: 'none' });

// Cinematic "color drain" on an image using ColorMatrixFilter convenience props:
gsap.timeline({ defaults: { duration: 1.5 } })
  .to(image, { pixi: { saturation: 0 } })
  .to(image, { pixi: { brightness: 1.4, contrast: 1.2 } });
```

## When to skip it
**Skip it entirely for normal HTML/CSS landing pages** — which is the default for everything this template builds. If the page's visuals are DOM elements (text, images, cards, sections), animate them with plain `gsap.to`/`gsap.from` plus `transform`/`opacity` as usual; PixiPlugin has nothing to offer there and adds an irrelevant script load. Only reach for it if the user explicitly wants a WebGL/canvas-rendered centerpiece (generative art, particle systems, game-like interactions) built with PixiJS — a genuinely niche, advanced request, not a default landing-page ingredient.
