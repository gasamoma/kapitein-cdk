/**
 * Captain AI — Lambda Function URL handler
 * Event format: payload format 2.0 (same as HTTP API Gateway)
 */

const { DynamoDBClient, PutItemCommand } = require("@aws-sdk/client-dynamodb");
const { randomUUID } = require("crypto");

const db = new DynamoDBClient({});

const HEADERS = {
  "Content-Type": "application/json",
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
};

exports.handler = async (event) => {
  const method = event.requestContext?.http?.method || "GET";
  const path   = event.rawPath || "/";

  console.log(`${method} ${path}`);

  if (method === "OPTIONS") {
    return { statusCode: 200, headers: HEADERS, body: "" };
  }

  if (method === "GET" && path === "/health") {
    return respond(200, { status: "healthy", table: process.env.TABLE_NAME });
  }

  if (method === "POST") {
    return handleLead(event);
  }

  return respond(200, { ok: true, message: "Captain AI API" });
};

async function handleLead(event) {
  let body;
  try {
    body = JSON.parse(event.body || "{}");
  } catch {
    return respond(400, { error: "Invalid JSON body" });
  }

  const { name, email, message, source, timestamp } = body;

  if (!name || !email) {
    return respond(400, { error: "name and email are required" });
  }

  const id  = randomUUID();
  const now = timestamp || new Date().toISOString();

  try {
    await db.send(new PutItemCommand({
      TableName: process.env.TABLE_NAME,
      Item: {
        PK:        { S: `LEAD#${email.toLowerCase()}` },
        SK:        { S: `SUBMISSION#${now}` },
        id:        { S: id },
        name:      { S: name },
        email:     { S: email },
        message:   { S: message || "" },
        source:    { S: source || "landing" },
        createdAt: { S: now },
      },
    }));

    console.log(`Lead saved: ${email}`);
    return respond(200, { ok: true, id });
  } catch (err) {
    console.error("DynamoDB error:", err);
    return respond(500, { error: "Failed to save lead" });
  }
}

function respond(statusCode, body) {
  return { statusCode, headers: HEADERS, body: JSON.stringify(body) };
}
