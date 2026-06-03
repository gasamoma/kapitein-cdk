/**
 * get-items.js — Queries DynamoDB and returns items for a given partition key.
 *
 * Copy this file to src/handlers/handler.js to use it.
 *
 * Expected GET request:
 *   GET /items?pk=contact
 *
 * Returns:
 *   200 { items: [...] }
 *   400 { error: "Missing query parameter: pk" }
 *   500 { error: "Internal server error" }
 *
 * Frontend usage:
 *   const res = await fetch(API_BASE_URL + "/items?pk=contact");
 *   const { items } = await res.json();
 */

import { DynamoDBClient, QueryCommand } from "@aws-sdk/client-dynamodb";
import { unmarshall } from "@aws-sdk/util-dynamodb";

const db = new DynamoDBClient({});

exports.handler = async (event) => {
  const method = event.requestContext?.http?.method;
  const params = event.queryStringParameters || {};

  if (method !== "GET") {
    return respond(405, { error: "Method not allowed" });
  }

  // Require the pk (partition key) query parameter
  const { pk } = params;
  if (!pk || pk.trim() === "") {
    return respond(400, { error: "Missing query parameter: pk" });
  }

  try {
    const result = await db.send(new QueryCommand({
      TableName: process.env.TABLE_NAME,
      // Query all items with this partition key
      KeyConditionExpression: "PK = :pk",
      ExpressionAttributeValues: {
        ":pk": { S: pk.trim() },
      },
      // Return newest items first (sort key is a timestamp-based string)
      ScanIndexForward: false,
      // Limit to 50 items per request
      Limit: 50,
    }));

    // Convert DynamoDB format ({ S: "value" }) to plain objects ({ key: "value" })
    const items = (result.Items || []).map(item => unmarshall(item));

    return respond(200, { items, count: items.length });
  } catch (err) {
    console.error("DynamoDB error:", err);
    return respond(500, { error: "Internal server error" });
  }
};

function respond(statusCode, body) {
  return {
    statusCode,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  };
}
