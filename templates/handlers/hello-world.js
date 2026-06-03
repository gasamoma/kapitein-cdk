/**
 * hello-world.js — Starter handler to verify your deployment is working.
 *
 * Copy this file to src/handlers/handler.js to use it.
 * Then push to main — GitHub Actions will deploy it.
 *
 * Test it: visit your CloudFront URL and check the API status line,
 * or call the API directly: GET https://<your-api-url>/
 */

exports.handler = async (event) => {
  const path   = event.rawPath || "/";
  const method = event.requestContext?.http?.method || "GET";

  console.log(`${method} ${path}`);

  return {
    statusCode: 200,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message: "Hello from your AWS Lambda function!",
      status:  "deployment confirmed working",
      path,
      method,
      tableName: process.env.TABLE_NAME,
      environment: process.env.ENVIRONMENT,
      timestamp: new Date().toISOString(),
    }),
  };
};
