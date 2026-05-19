import os
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    CfnOutput,
    RemovalPolicy,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    aws_lambda_nodejs as nodejs_lambda,
    aws_apigatewayv2 as apigwv2,
)
from aws_cdk.aws_apigatewayv2_integrations import HttpLambdaIntegration
from constructs import Construct
from kapitein_cdk import WebAppConstruct

# Path to the handlers directory relative to this file
HANDLERS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "handlers")
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src", "frontend")


class WebsiteStack(Stack):
    """
    Full serverless website stack: CloudFront + S3 + HTTP API + Lambda + DynamoDB.

    Deploys:
      - S3 bucket (private, accessed via CloudFront)
      - CloudFront distribution (HTTPS, gzip, SPA routing)
      - HTTP API Gateway (v2)
      - Lambda function (Node.js 20, Docker-bundled)
      - DynamoDB table (on-demand, PK + SK)

    Frontend files go in src/frontend/.
    Lambda handler goes in src/handlers/handler.js.
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # DynamoDB table — flexible schema with PK + SK
        table = dynamodb.Table(
            self,
            "Table",
            partition_key=dynamodb.Attribute(name="PK", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="SK", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.RETAIN,
        )

        # Lambda function — always bundled in Docker so no local Node.js is needed
        api_handler = nodejs_lambda.NodejsFunction(
            self,
            "ApiHandler",
            entry=os.path.join(HANDLERS_DIR, "handler.js"),
            handler="handler",
            runtime=lambda_.Runtime.NODEJS_20_X,
            bundling=nodejs_lambda.BundlingOptions(
                force_docker_bundling=True,
                external_modules=["@aws-sdk/*"],
            ),
            environment={
                "TABLE_NAME": table.table_name,
                "ENVIRONMENT": "production",
            },
            timeout=cdk.Duration.seconds(30),
        )

        table.grant_read_write_data(api_handler)

        # HTTP API Gateway — cheaper and simpler than REST API
        http_api = apigwv2.HttpApi(
            self,
            "Api",
            cors_preflight=apigwv2.CorsPreflightOptions(
                allow_origins=["*"],
                allow_methods=[apigwv2.CorsHttpMethod.ANY],
                allow_headers=["Content-Type", "Authorization"],
                max_age=cdk.Duration.days(1),
            ),
        )

        http_api.add_routes(
            path="/{proxy+}",
            methods=[apigwv2.HttpMethod.ANY],
            integration=HttpLambdaIntegration("HandlerIntegration", api_handler),
        )

        # CloudFront + S3 frontend — inject API URL as config.json
        web_app = WebAppConstruct(
            self,
            "WebApp",
            source_path=FRONTEND_DIR,
            config_data={
                "apiUrl": http_api.url,
            },
            enable_spa_routing=True,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # Stack outputs — visible in GitHub Actions summary and CloudFormation console
        CfnOutput(self, "WebsiteUrl", value=web_app.url, description="CloudFront URL — open this in your browser")
        CfnOutput(self, "ApiUrl", value=http_api.url, description="API Gateway URL")
        CfnOutput(self, "TableName", value=table.table_name, description="DynamoDB table name")
