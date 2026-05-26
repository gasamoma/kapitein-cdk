# Claude Code — Project Interview Template

> **Instructions for use:**
> Copy this file into your project folder as `CLAUDE.md`.
> Then open Claude Code in that folder and type: **Start a new project**
>
> Claude will interview you before writing any code.
>
> If you already know what kind of site you want, consider using one of the
> specialized templates in `templates/agents/` instead — they skip the interview
> and start building immediately.

---

When the user says "Start a new project", run the following interview. Ask one question at a time and wait for the answer before moving to the next.

## Interview Questions

**Question 1:**
"What kind of website do you want to build? For example: a portfolio showing your work, a business site for a service you offer, a landing page for a product, a blog, or something else?"

Wait for the answer, then ask:

**Question 2 — the architecture question:**
"Does your site need user accounts? In other words: will visitors need to register and log in to see content or access features that are personal to them — like a dashboard, saved items, or a member area?

Or can everyone who visits the site see the same content, without logging in? For example, a contact form, a portfolio, or a product page — anyone can use it, no account needed.

This is important because it changes how the site is built. There's no wrong answer."

Wait for the answer. Based on the answer, note internally which path applies:
- **No login needed** → Public site (always-free tier: Lambda Function URL + DynamoDB)
- **Login needed** → Authenticated site (Cognito + API Gateway; free for 12 months, then small costs)

If the user chose the **authenticated** path, add this follow-up:
"Got it — your site will need user accounts. Just so you know: the login system (AWS Cognito) is free for the first 12 months, then costs around $0.0055 per monthly active user — so 100 regular users would be about $0.55/month. That's very affordable, but I want you to know upfront. Does that work for you?"

Then ask:

**Question 3:**
"Who is this site for? Describe your ideal visitor in plain language — don't worry about using marketing terms."

Wait for the answer, then ask:

**Question 4:**
"What's the most important thing you want visitors to do when they land on your site? For example: book a call, buy a product, read your story, sign up, contact you."

Wait for the answer, then ask:

**Question 5:**
"How should the site feel? You can use words like: clean and minimal, warm and friendly, bold and confident, elegant and premium — or describe it in your own words. Also: should it have animations and motion (like elements fading in as you scroll), or keep it calm and still?"

Wait for the answer, then ask:

**Question 6:**
"What pages does your site need? For example: Home, About, Services, Portfolio, Contact."

---

## After All Six Answers

Summarize the project in 3–4 sentences — including which type of site it is (public or authenticated) and why — and ask:
"Does this capture what you're building? Tell me anything I got wrong or missed."

After the user confirms, say:
"Type **write the spec** and I'll create a CLAUDE.md that captures everything for future reference."

When the user says "write the spec", create a `CLAUDE.md` file with:
1. A plain-English description of the project
2. The target audience and goal
3. The visual style (including animation preference)
4. The page list
5. The architecture section below — use the **Public site** section if no login is needed, or the **Authenticated site** section if login is needed

---

## Architecture Reference — Public Site (no user accounts)

Use this section when the user said they do NOT need user login.

**Stack:** `WebAppConstruct` + `PublicApiConstruct` + DynamoDB
**Cost:** Always free (Lambda Function URL + DynamoDB both in the always-free tier)

### Frontend

Static files go in `src/frontend/`.
- `src/frontend/index.html` is the entry point
- CSS files go in `src/frontend/css/`
- JavaScript files go in `src/frontend/js/`
- Images go in `src/frontend/images/`

Plain HTML, CSS, and JavaScript is the default. Do not add a build step unless explicitly asked.

To get the API URL in JavaScript:
```js
fetch("/config.json")
  .then(r => r.json())
  .then(config => { window.API_BASE_URL = config.apiUrl; });
```

### CDN Libraries (use freely — no build step needed)

**GSAP** — animations and scroll effects:
```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/ScrollTrigger.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/SplitText.min.js"></script>
```

**Alpine.js** — interactive UI without a build step:
```html
<script src="https://cdn.jsdelivr.net/npm/alpinejs@3/dist/cdn.min.js" defer></script>
```

Use GSAP when the user asked for motion, scroll effects, or a "modern" feel.

### Backend (Lambda — always free)

File: `src/handlers/handler.js`

```js
exports.handler = async (event, context) => {
  const path   = event.rawPath;
  const method = event.requestContext.http.method;
  const body   = event.body ? JSON.parse(event.body) : {};

  return {
    statusCode: 200,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ok: true })
  };
};
```

Note: Lambda Function URLs use the same event format as API Gateway HTTP API v2.

### Database (DynamoDB — always free)

```js
import { DynamoDBClient, PutItemCommand, QueryCommand } from "@aws-sdk/client-dynamodb";
const db = new DynamoDBClient({});
// TABLE_NAME is injected automatically by the CDK stack
```

### CORS

CORS is handled by the Lambda Function URL configuration. Do not add CORS headers manually.

### Deploying

Push to `main`. GitHub Actions deploys automatically. Do not instruct the user to run AWS or CDK commands locally.

---

## Architecture Reference — Authenticated Site (user accounts + login)

Use this section when the user said they DO need user login.

**Stack:** `WebAppConstruct` + `CognitoWebPortalConstruct` + `AuthorizedApiConstruct` + DynamoDB
**Cost:** Free for 12 months (Cognito + API Gateway are on the 12-month free tier); after that, approximately $0.0055 per monthly active user

### What changes vs a public site

1. Users register and log in via AWS Cognito (hosted login page, no code needed)
2. The API Gateway checks the Cognito token on every request — unauthenticated requests are rejected automatically
3. The frontend gets the Cognito client ID from `config.json` and uses it to manage the login flow

### Frontend

Same file locations as the public site (`src/frontend/`).

Get both the API URL and Cognito config from `config.json`:
```js
fetch("/config.json")
  .then(r => r.json())
  .then(config => {
    window.API_BASE_URL   = config.apiUrl;
    window.COGNITO_CLIENT = config.cognitoClientId;
    window.COGNITO_DOMAIN = config.cognitoDomain;
  });
```

To log users in, redirect them to the Cognito hosted UI:
```js
const loginUrl = `https://${window.COGNITO_DOMAIN}/login`
  + `?client_id=${window.COGNITO_CLIENT}`
  + `&response_type=token`
  + `&redirect_uri=${encodeURIComponent(window.location.origin)}`;
window.location.href = loginUrl;
```

After login, Cognito redirects back with an `id_token` in the URL fragment. Pass it as a Bearer token on API calls:
```js
const token = new URLSearchParams(window.location.hash.slice(1)).get("id_token");
const res = await fetch(window.API_BASE_URL + "/my-data", {
  headers: { Authorization: `Bearer ${token}` }
});
```

### Backend (Lambda — behind Cognito auth)

File: `src/handlers/handler.js` — same event format as the public site.
The Cognito user's details are available in the JWT claims passed by API Gateway:
```js
exports.handler = async (event) => {
  // API Gateway validates the token — if we get here, the user is authenticated
  const claims = event.requestContext?.authorizer?.jwt?.claims || {};
  const userId  = claims.sub;   // unique Cognito user ID
  const email   = claims.email;

  // use userId as the DynamoDB partition key to keep data per-user
  return { statusCode: 200, headers: { "Content-Type": "application/json" }, body: JSON.stringify({ userId }) };
};
```

### CORS

`AuthorizedApiConstruct` configures CORS automatically. Do not add CORS headers manually.

### Deploying

Push to `main`. GitHub Actions deploys automatically. Do not instruct the user to run AWS or CDK commands locally.
