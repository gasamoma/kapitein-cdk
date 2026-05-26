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
"What kind of website do you want to build? For example: a portfolio showing your work, a business site for a service you offer, a landing page for a product, or something else?"

Wait for the answer, then ask:

**Question 2:**
"Who is this site for? Describe your ideal visitor in plain language — don't worry about using marketing terms."

Wait for the answer, then ask:

**Question 3:**
"What's the most important thing you want visitors to do when they land on your site? For example: book a call, buy a product, read your story, contact you."

Wait for the answer, then ask:

**Question 4:**
"How should the site feel? You can use words like: clean and minimal, warm and friendly, bold and confident, elegant and premium — or describe it in your own words. Also tell me: should it have animations and motion (like elements fading in as you scroll), or stay calm and still?"

Wait for the answer, then ask:

**Question 5:**
"What pages does your site need? For example: Home, About, Services, Portfolio, Contact."

## After All Five Answers

Summarize the project in 3–4 sentences and ask:
"Does this capture what you're building? Tell me anything I got wrong or missed."

After the user confirms, say:
"Type **write the spec** and I'll create a CLAUDE.md that captures everything for future reference."

When the user says "write the spec", create a `CLAUDE.md` file with:
1. A plain-English description of the project
2. The target audience and goal
3. The visual style (including whether animations are wanted)
4. The page list
5. The architecture section below (copy it in full)

---

## Architecture Reference

You are building on the **kapitein-cdk** serverless AWS stack. Follow these conventions exactly.

### Frontend

Static files go in `src/frontend/`.
- `src/frontend/index.html` is the entry point
- CSS files go in `src/frontend/css/`
- JavaScript files go in `src/frontend/js/`
- Images go in `src/frontend/images/`

Plain HTML, CSS, and JavaScript is the default. Do not add a build step unless the user explicitly asks for a framework that requires one.

To get the API URL in JavaScript:

```js
fetch("/config.json")
  .then(r => r.json())
  .then(config => {
    window.API_BASE_URL = config.apiUrl;
  });
```

### CDN Libraries (use freely)

Libraries loaded via `<script>` CDN tags work with no build step and deploy instantly.

**GSAP** — for animations, scroll effects, text animations:
```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/ScrollTrigger.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15/dist/SplitText.min.js"></script>
```

**Alpine.js** — for interactive UI (tabs, modals, dropdowns):
```html
<script src="https://cdn.jsdelivr.net/npm/alpinejs@3/dist/cdn.min.js" defer></script>
```

**PicoCSS** — beautiful semantic defaults, no utility classes needed:
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
```

Use GSAP animations when the user asked for motion, scroll effects, or a "modern" feel. Use Alpine.js for interactive components. Use PicoCSS or custom CSS for styling — avoid Tailwind CDN on production sites.

### Backend (Lambda)

Lambda handler file: `src/handlers/handler.js`

```js
exports.handler = async (event, context) => {
  return {
    statusCode: 200,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: "Hello!" })
  };
};
```

- `event.rawPath` → the URL path (e.g. `/contact`)
- `event.requestContext.http.method` → `"GET"` or `"POST"`
- `event.body` → request body string (use `JSON.parse(event.body)` to read it)
- `event.queryStringParameters` → object of `?key=value` params

### Database (DynamoDB)

Table name: `process.env.TABLE_NAME`

```js
import { DynamoDBClient, PutItemCommand, QueryCommand } from "@aws-sdk/client-dynamodb";
const db = new DynamoDBClient({});
```

### Deploying

Users push to the `main` branch. GitHub Actions handles the deployment automatically.
Do not tell the user to run `cdk deploy` — they don't have AWS CLI set up locally.

### CORS

CORS is handled automatically by API Gateway. Do not add CORS headers manually in Lambda.
