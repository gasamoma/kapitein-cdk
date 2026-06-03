import os
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    CfnOutput,
    RemovalPolicy,
    aws_dynamodb as dynamodb,
)
from constructs import Construct
from kapitein_cdk import WebAppConstruct, PublicApiConstruct

HANDLERS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "handlers")
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "frontend")


class WebsiteStack(Stack):
    """
    Public website stack — always-free tier.

    Uses Lambda Function URL instead of API Gateway so the backend stays
    in the always-free tier (1M requests/month forever).

    For a site that needs user accounts and login, use a stack based on
    CognitoWebPortalConstruct + AuthorizedApiConstruct instead.

    Frontend files: src/frontend/
    Lambda handler:  src/handlers/handler.js
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # DynamoDB table — always free (25 GB, 25 WCU/RCU forever)
        table = dynamodb.Table(
            self,
            "Table",
            partition_key=dynamodb.Attribute(name="PK", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="SK", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN,
        )

        # Lambda + Function URL — always free, no API Gateway needed
        api = PublicApiConstruct(
            self,
            "Api",
            entry=os.path.join(HANDLERS_DIR, "handler.js"),
            environment={
                "TABLE_NAME": table.table_name,
                "ENVIRONMENT": "production",
            },
        )

        table.grant_read_write_data(api.function)

        # CloudFront + S3 — injects the Lambda URL into config.json at deploy time
        web_app = WebAppConstruct(
            self,
            "WebApp",
            source_path=FRONTEND_DIR,
            config_data={"apiUrl": api.url},
            enable_spa_routing=True,
            removal_policy=RemovalPolicy.DESTROY,
        )

        CfnOutput(self, "WebsiteUrl", value=web_app.url, description="CloudFront URL — open this in your browser")
        CfnOutput(self, "ApiUrl", value=api.url, description="Lambda Function URL")
        CfnOutput(self, "TableName", value=table.table_name, description="DynamoDB table name")
