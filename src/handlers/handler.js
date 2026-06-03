/**
 * Default Lambda handler — replace this with your own logic.
 *
 * Event format: Lambda Function URL (payload format 2.0 — same as HTTP API Gateway)
 * - event.rawPath        → e.g. "/hello"
 * - event.requestContext.http.method → "GET", "POST", etc.
 * - event.body           → request body string (JSON.parse it)
 * - event.queryStringParameters → query params object
 *
 * Environment variables available:
 * - process.env.TABLE_NAME  → DynamoDB table name
 * - process.env.ENVIRONMENT → "production"
 */

exports.handler = async (event) => {
  const path = event.rawPath || "/";
  const method = event.requestContext?.http?.method || "GET";

  console.log(`${method} ${path}`);

  // Route requests
  if (method === "GET" && path === "/") {
    return respond(200, { message: "Hello from your website API!", status: "ok" });
  }

  if (method === "GET" && path === "/health") {
    return respond(200, { status: "healthy", tableName: process.env.TABLE_NAME });
  }

  return respond(404, { error: "Not found", path });
};

function respond(statusCode, body) {
  return {
    statusCode,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  };
}
