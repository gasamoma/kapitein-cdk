/**
 * contact-form.js — Accepts a contact form POST and saves it to DynamoDB.
 *
 * Copy this file to src/handlers/handler.js to use it.
 *
 * Expected POST body (JSON):
 *   { "name": "Alice", "email": "alice@example.com", "message": "Hi!" }
 *
 * Returns:
 *   200 { success: true }
 *   400 { error: "Missing required field: name" }
 *   500 { error: "Internal server error" }
 *
 * Frontend usage:
 *   const res = await fetch(API_BASE_URL + "/contact", {
 *     method: "POST",
 *     headers: { "Content-Type": "application/json" },
 *     body: JSON.stringify({ name, email, message })
 *   });
 */

import { DynamoDBClient, PutItemCommand } from "@aws-sdk/client-dynamodb";

const db = new DynamoDBClient({});

exports.handler = async (event) => {
  const method = event.requestContext?.http?.method;

  if (method !== "POST") {
    return respond(405, { error: "Method not allowed" });
  }

  // Parse the request body
  let body;
  try {
    body = JSON.parse(event.body || "{}");
  } catch {
    return respond(400, { error: "Invalid JSON in request body" });
  }

  // Validate required fields
  const { name, email, message } = body;
  for (const field of ["name", "email", "message"]) {
    if (!body[field] || String(body[field]).trim() === "") {
      return respond(400, { error: `Missing required field: ${field}` });
    }
  }

  // Basic email format check
  if (!email.includes("@")) {
    return respond(400, { error: "Invalid email address" });
  }

  // Save to DynamoDB
  const timestamp = new Date().toISOString();
  const id = `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;

  try {
    await db.send(new PutItemCommand({
      TableName: process.env.TABLE_NAME,
      Item: {
        PK:        { S: "contact" },
        SK:        { S: `${timestamp}#${id}` },
        name:      { S: String(name).trim() },
        email:     { S: String(email).trim().toLowerCase() },
        message:   { S: String(message).trim() },
        createdAt: { S: timestamp },
      },
    }));
  } catch (err) {
    console.error("DynamoDB error:", err);
    return respond(500, { error: "Internal server error" });
  }

  return respond(200, { success: true });
};

function respond(statusCode, body) {
  return {
    statusCode,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  };
}
