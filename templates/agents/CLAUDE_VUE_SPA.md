# Vue.js SPA Agent — kapitein-cdk

You are building a Vue.js single-page application using the kapitein-cdk serverless stack.
The CDK stack will build and bundle the Vue app inside Docker on GitHub Actions — the user does not need Node.js locally to deploy.

## Your job

Build a Vue.js SPA in `src/frontend/`. Enable the Docker build in the CDK stack. When finished, remind the user to push to `main` to deploy.

Ask the user:
1. What is this application for?
2. What are the main screens or views? (e.g. Dashboard, Profile, Settings)
3. Does it need user authentication? (if yes, note that Cognito integration is available via `CognitoWebPortalConstruct`)
4. What data does it need to read and write?

After getting answers, scaffold the full app without further questions.

---

## Stack

### Enabling the Vue build in CDK

Edit `stacks/website_stack.py` and change the `WebAppConstruct` call to enable the Docker build:

```python
web_app = WebAppConstruct(
    self, "WebApp",
    source_path=FRONTEND_DIR,
    config_data={"apiUrl": http_api.url},
    enable_build=True,          # runs npm ci && npm run build inside Docker
    build_image="node:22-alpine",
    removal_policy=RemovalPolicy.DESTROY,
)
```

The build runs `npm ci --include=dev` then `npm run build` inside a Docker container on GitHub Actions. Output must go to `dist/`. The CDK construct copies `dist/*` to S3.

### Project structure

```
src/frontend/
├── index.html          # Vite entry point
├── package.json        # Vue + Vite deps
├── vite.config.js      # Vite config
└── src/
    ├── main.js
    ├── App.vue
    ├── router/index.js
    └── views/
        ├── HomeView.vue
        └── ...
```

### Scaffold command (run this once locally, or ask Claude Code to generate the files)

```bash
npm create vue@latest . -- --router --no-typescript --no-pinia --no-vitest --no-eslint
```

Or generate all files manually without running shell commands.

### Getting the API URL into Vue

The CDK stack injects `config.json` into the S3 bucket at deploy time. Fetch it at app startup:

```js
// src/main.js
import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";

fetch("/config.json")
  .then(r => r.json())
  .then(config => {
    const app = createApp(App);
    app.provide("apiUrl", config.apiUrl);  // inject into all components
    app.use(router);
    app.mount("#app");
  });
```

Access in components:
```vue
<script setup>
import { inject } from "vue";
const apiUrl = inject("apiUrl");

async function fetchData() {
  const res = await fetch(apiUrl + "/items?pk=myKey");
  const { items } = await res.json();
}
</script>
```

### Vite config

```js
// vite.config.js
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  build: { outDir: "dist" }  // CDK expects output in dist/
});
```

### package.json build script (must be present)

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.3.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^5.2.0"
  }
}
```

### Calling the API

```js
// src/api.js — a reusable API helper
let baseUrl = null;
export function setApiUrl(url) { baseUrl = url; }

export async function apiPost(path, data) {
  const res = await fetch(baseUrl + path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function apiGet(path, params = {}) {
  const qs = new URLSearchParams(params).toString();
  const res = await fetch(baseUrl + path + (qs ? "?" + qs : ""));
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}
```

### Lambda backend (unchanged — still in src/handlers/handler.js)

The Vue build only affects the frontend. Lambda handler, DynamoDB, and API Gateway work exactly as in the plain-HTML stack.

```js
exports.handler = async (event) => {
  const path   = event.rawPath;
  const method = event.requestContext.http.method;
  const body   = event.body ? JSON.parse(event.body) : {};
  const params = event.queryStringParameters || {};

  // add your routing here
  return { statusCode: 200, headers: { "Content-Type": "application/json" }, body: JSON.stringify({ ok: true }) };
};
```

### CORS
API Gateway allows all origins. Do not add CORS headers in Lambda.

### Deploying
User pushes to `main`. GitHub Actions runs the Docker build and deploys automatically.
Build + deploy takes approximately 8–15 minutes on first run due to Docker image pull and npm install.

---

## Important constraints

- Keep `dist/` in `.gitignore` — it's built in the cloud, not committed
- The `index.html` at the root of `src/frontend/` is Vite's template; Vite replaces it with the built version in `dist/`
- If the user needs Cognito auth, use `CognitoWebPortalConstruct` in the CDK stack and inject `cognitoClientId` and `cognitoUserPoolId` via `config_data` in the same way as `apiUrl`
