# Architecture Context — kapitein-cdk Stack

Include this section in your project's `CLAUDE.md` so Claude Code knows how to build for this stack.
Choose the section that matches your site type.

---

## Public Site (no user accounts) — always-free tier

**Constructs:** `WebAppConstruct` + `PublicApiConstruct` + DynamoDB

All three AWS services used are in the **always-free tier**: Lambda (1M requests/month forever), DynamoDB (25 GB + 25 WCU/RCU forever), CloudFront (1 TB transfer + 10M requests/month forever).

### Frontend

Static files in `src/frontend/` → deployed to S3 → served via CloudFront.

- `src/frontend/index.html` — entry point
- `src/frontend/css/` — stylesheets
- `src/frontend/js/` — scripts
- `src/frontend/images/` — images and fonts

Plain HTML, CSS, and JavaScript preferred. No build step required.

The CDK stack injects `config.json` at deploy time — read it to get the API URL:

```js
let API_BASE_URL;
fetch("/config.json")
  .then(r => r.json())
  .then(config => { API_BASE_URL = config.apiUrl; });
```

### CDN Libraries (use freely)

Libraries via `<script>` CDN tags work with no build step and deploy instantly.

**GSAP** — animations, scroll effects, text animations:
```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/ScrollTrigger.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/SplitText.min.js"></script>
```
```js
gsap.registerPlugin(ScrollTrigger, SplitText);
gsap.from(".hero-title", { opacity: 0, y: 60, duration: 1 });
gsap.utils.toArray(".reveal").forEach(el =>
  gsap.from(el, { opacity: 0, y: 40, duration: 0.7,
    scrollTrigger: { trigger: el, start: "top 85%" } })
);
```

**Alpine.js** — interactive UI (tabs, modals, accordions):
```html
<script src="https://cdn.jsdelivr.net/npm/alpinejs@3/dist/cdn.min.js" defer></script>
```

**PicoCSS** — semantic defaults, no utility classes:
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
```

### Backend (Lambda via Function URL)

File: `src/handlers/handler.js` — uses API Gateway HTTP API v2 event format.

```js
exports.handler = async (event, context) => {
  const path   = event.rawPath;
  const method = event.requestContext.http.method;
  const body   = event.body ? JSON.parse(event.body) : {};
  const params = event.queryStringParameters || {};

  return {
    statusCode: 200,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ok: true })
  };
};
```

CORS is configured on the Function URL — do not add CORS headers manually.

### Database (DynamoDB)

`process.env.TABLE_NAME` — always available in the Lambda environment.
Primary key: `PK` (string), sort key: `SK` (string).

```js
import { DynamoDBClient, PutItemCommand, QueryCommand } from "@aws-sdk/client-dynamodb";
const db = new DynamoDBClient({});
```

### Framework builds (Vue / React)

If a framework requiring a build step is genuinely needed, enable it in `stacks/website_stack.py`:

```python
web_app = WebAppConstruct(
    self, "WebApp",
    source_path=FRONTEND_DIR,
    config_data={"apiUrl": api.url},
    enable_build=True,
    build_image="node:22-alpine",   # runs npm ci && npm run build inside Docker
    removal_policy=RemovalPolicy.DESTROY,
)
```

Output must go to `dist/`. Build runs on GitHub Actions — users still need no local Node.js.

---

## Authenticated Site (user accounts + login) — 12-month free tier

**Constructs:** `WebAppConstruct` + `CognitoWebPortalConstruct` + `AuthorizedApiConstruct` + DynamoDB

Cognito and API Gateway are on the **12-month free tier** (not always-free). After 12 months: ~$0.0055 per monthly active user.

### Frontend

Same file locations as the public site.

`config.json` is injected with both the API URL and Cognito config:

```js
fetch("/config.json")
  .then(r => r.json())
  .then(config => {
    window.API_BASE_URL   = config.apiUrl;
    window.COGNITO_CLIENT = config.cognitoClientId;
    window.COGNITO_DOMAIN = config.cognitoDomain;
  });
```

**Login redirect** — send the user to the Cognito hosted UI:
```js
const loginUrl = `https://${window.COGNITO_DOMAIN}/login`
  + `?client_id=${window.COGNITO_CLIENT}`
  + `&response_type=token`
  + `&redirect_uri=${encodeURIComponent(window.location.origin)}`;
window.location.href = loginUrl;
```

**After login** — Cognito redirects back with `id_token` in the URL fragment:
```js
const token = new URLSearchParams(window.location.hash.slice(1)).get("id_token");
localStorage.setItem("id_token", token);
```

**Authenticated API calls** — pass the token as a Bearer header:
```js
const res = await fetch(window.API_BASE_URL + "/my-data", {
  headers: { Authorization: `Bearer ${localStorage.getItem("id_token")}` }
});
```

### Backend (Lambda behind Cognito auth)

API Gateway validates the Cognito token before the Lambda runs — unauthenticated requests are rejected automatically. Cognito user details arrive in the event:

```js
exports.handler = async (event) => {
  const claims = event.requestContext?.authorizer?.jwt?.claims || {};
  const userId  = claims.sub;   // unique Cognito user ID — use as DynamoDB PK
  const email   = claims.email;

  return {
    statusCode: 200,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ userId, email })
  };
};
```

CORS is configured by `AuthorizedApiConstruct` — do not add CORS headers manually.

### Deployment

Push to `main`. GitHub Actions deploys automatically for both site types.
Do not instruct users to run any AWS or CDK commands locally.
