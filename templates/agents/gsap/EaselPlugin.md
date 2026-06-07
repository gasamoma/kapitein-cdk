# EaselPlugin

## What it's for

EaselPlugin lets GSAP tween special CreateJS/EaselJS canvas properties — `saturation`, `contrast`, `tint`, `colorize`, `brightness`, `exposure`, `hue` (powered by EaselJS's `ColorFilter`/`ColorMatrixFilter`), plus the `frame` property of a `MovieClip`. **It is exclusively for projects that render through EaselJS's canvas/stage API.** If your landing page is built with normal HTML/CSS/DOM elements (which is the default for this project), this plugin does nothing useful for you — skip straight to the "When to skip it" section.

## Setup

```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/EaselPlugin.min.js"></script>
<script>
  gsap.registerPlugin(EaselPlugin);
</script>
```

**Hard dependency: EaselJS itself**, plus its `ColorFilter`/`ColorMatrixFilter` scripts must be loaded — the plugin only adds GSAP integration on top of an existing EaselJS stage; it doesn't provide canvas rendering itself.

## Key concepts

- **You don't need this plugin for ordinary EaselJS properties.** Plain numeric properties like `x`, `y`, `scaleX`, `rotation` already tween fine with vanilla `gsap.to()`. EaselPlugin exists only for the *special* color/filter properties that need extra translation into EaselJS's filter objects.
- **All special properties must be wrapped in an `easel: {}` object** — this is how you signal "these aren't plain object properties, translate them through EaselJS's filter system."
- **The element must be `.cache()`d for `ColorFilter` effects (like `tint`) to render at all** — this is an EaselJS requirement, not a GSAP one, but it's the most common reason a tint/colorize tween appears to "do nothing."
- **You can tween convenience properties GreenSock added on top of the raw EaselJS API** — `tint`, `tintAmount`, `exposure`, `brightness` (for `ColorFilter`), and `saturation`, `hue`, `contrast`, `colorize`, `colorizeAmount` (for `ColorMatrixFilter`) — or drop down to raw `ColorFilter` properties directly via `easel: { colorFilter: { redMultiplier, blueMultiplier, greenOffset, ... } }`.
- **Don't forget the EaselJS render loop** — tweening these properties updates the underlying model, but you still need something like `gsap.ticker.add(() => stage.update())` for the canvas to actually repaint each frame (this is standard EaselJS practice, not GSAP-specific).

## Common gotchas

- Forgetting to wrap properties in `easel: {}` is, per the official docs, "a common mistake" — without it, GSAP has no way to know these aren't plain object properties to set directly.
- Forgetting to `.cache()` the display object before tweening `ColorFilter`-backed properties (`tint`, `exposure`, `brightness`, etc.) means the filter never gets applied visually.
- `exposure` and `brightness` both use a 0–2 scale where `1` is "normal" — easy to misread as a 0–1 percentage and end up with values that look wrong.

## Recipes

Not applicable — recipes for this plugin only make sense inside an EaselJS canvas/stage setup, which is fundamentally different from the DOM-based, transform/opacity-driven animation approach this project uses for landing pages. See the official docs (`gsap.com/docs/v3/Plugins/EaselPlugin/`) for canvas-context examples if a project specifically requires EaselJS.

## When to skip it

**Skip this plugin for virtually every landing page you'll build in this project.** It is irrelevant unless the page is rendering through an EaselJS `<canvas>` stage (e.g. a game, a generative-art piece, a canvas-based interactive demo) — which a standard HTML/CSS/JS marketing/landing page never is. For visual color effects on normal DOM elements (images, backgrounds, gradients), use CSS filters (`filter: saturate() / brightness() / hue-rotate()`) animated via plain `gsap.to()`, which is dramatically simpler, has no canvas/EaselJS dependency, and stays consistent with the project's transform/opacity performance principle.
