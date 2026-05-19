# Architecture Context — kapitein-cdk Stack

Include this section in your project's `CLAUDE.md` so Claude Code knows how to build for this stack.

---

## Stack Architecture

You are building on the **kapitein-cdk** serverless stack. Here is how it works:

### Frontend

Static files in `src/frontend/` are deployed to S3 and served via CloudFront.

- `src/frontend/index.html` is the entry point
- CSS and JS go in `src/frontend/css/` and `src/frontend/js/`
- Do not use React, Vue, or any framework requiring a build step unless asked

The CDK stack injects a `config.json` file into the S3 bucket at deploy time.
Read it on page load to get the API URL:

```js
let API_BASE_URL;
fetch("/config.json")
  .then(r => r.json())
  .then(config => { API_BASE_URL = config.apiUrl; });
```

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
Do not instruct the user to run any AWS CLI or CDK commands locally — they don't have those tools set up.
The deployment takes 5–10 minutes on first run, 2–5 minutes after that.
