# Architecture Context — kapitein-cdk Stack

Include this section in your project's `CLAUDE.md` so Claude Code knows how to build for this stack.

---

## Stack Architecture

You are building on the **kapitein-cdk** serverless stack. Here is how it works:

### Frontend

Static files in `src/frontend/` are deployed to S3 and served via CloudFront.

- `src/frontend/index.html` is the entry point
- CSS and JS go in `src/frontend/css/` and `src/frontend/js/`
- Images and fonts go in `src/frontend/images/` and `src/frontend/fonts/`
- Plain HTML/CSS/JS is preferred — no build step required
- For a Vue.js or React SPA that needs a build step, see the "Framework builds" section below

The CDK stack injects a `config.json` file into the S3 bucket at deploy time.
Read it on page load to get the API URL:

```js
let API_BASE_URL;
fetch("/config.json")
  .then(r => r.json())
  .then(config => { API_BASE_URL = config.apiUrl; });
```

### CDN Libraries (encouraged)

Any library that can be loaded from a CDN `<script>` tag works without a build step.
These are preferred because they deploy instantly without any Docker bundling.

**Animation — GSAP** (GreenSock): smooth, performant animations and scroll effects

```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/ScrollTrigger.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/SplitText.min.js"></script>
<script>
  document.addEventListener("DOMContentLoaded", () => {
    gsap.registerPlugin(ScrollTrigger, SplitText);
    // animate elements as they scroll into view
    gsap.from(".hero-title", { opacity: 0, y: 60, duration: 1 });
    gsap.from(".card", {
      opacity: 0, y: 40, stagger: 0.15, duration: 0.8,
      scrollTrigger: { trigger: ".cards", start: "top 80%" }
    });
  });
</script>
```

**Lightweight reactivity — Alpine.js**: add interactivity (tabs, modals, dropdowns) without a build step

```html
<script src="https://cdn.jsdelivr.net/npm/alpinejs@3/dist/cdn.min.js" defer></script>
<div x-data="{ open: false }">
  <button @click="open = !open">Toggle</button>
  <div x-show="open">Content</div>
</div>
```

**CSS frameworks — Tailwind CDN** (for prototyping) or **PicoCSS** (classless, semantic)

```html
<!-- Tailwind play CDN — fast for prototyping, use production build for prod -->
<script src="https://cdn.tailwindcss.com"></script>

<!-- PicoCSS — beautiful defaults, no classes needed -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
```

### Framework builds (Vue / React)

If a framework that requires a build step is genuinely needed, `WebAppConstruct` supports Docker-based builds via `enable_build=True`. The build runs on GitHub Actions — users still don't need Node.js locally.

To enable it, update `stacks/website_stack.py`:

```python
web_app = WebAppConstruct(
    self, "WebApp",
    source_path=FRONTEND_DIR,
    config_data={"apiUrl": http_api.url},
    enable_build=True,          # triggers npm ci && npm run build inside Docker
    build_image="node:22-alpine",
    removal_policy=RemovalPolicy.DESTROY,
)
```

The frontend `src/frontend/` directory must then contain a standard `package.json` with a `build` script that outputs to `dist/`. The CDK construct copies `dist/*` to S3.

Only enable this when CDN-loaded libraries genuinely cannot meet the requirement. The Docker build step adds 3–5 minutes to every deployment.

### Backend

Lambda functions in `src/handlers/` handle API requests.

**File:** `src/handlers/handler.js`
**Export:** `exports.handler = async (event, context) => { ... }`

The `event` object is an API Gateway v2 payload (HTTP API format):

```js
exports.handler = async (event, context) => {
  const path   = event.rawPath;                          // e.g. "/contact"
  const method = event.requestContext.http.method;       // "GET" | "POST" | ...
  const body   = event.body ? JSON.parse(event.body) : {};
  const params = event.queryStringParameters || {};

  return {
    statusCode: 200,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ok: true })
  };
};
```

### Database

DynamoDB table available in Lambda via `process.env.TABLE_NAME`.
Primary key: `PK` (string), sort key: `SK` (string).

Use the AWS SDK v3 (pre-installed in Node.js 20 Lambda runtime):

```js
import { DynamoDBClient, PutItemCommand, QueryCommand, GetItemCommand } from "@aws-sdk/client-dynamodb";
const db = new DynamoDBClient({});
```

### Calling the API from the Frontend

```js
// POST example
const response = await fetch(API_BASE_URL + "/contact", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ name: "Alice", email: "alice@example.com", message: "Hi!" })
});
const data = await response.json();
```

### CORS

API Gateway is configured to allow requests from any origin. Do not add CORS headers manually.

### Deployment

Users push to the `main` branch on GitHub. GitHub Actions runs `cdk deploy` automatically.
Do not instruct the user to run any AWS CLI or CDK commands locally.
The deployment takes 5–10 minutes on first run, 2–5 minutes after that.
