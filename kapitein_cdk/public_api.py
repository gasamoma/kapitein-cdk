"""
Reusable CDK L3 Construct for a publicly accessible Lambda API via Function URL.

No authentication — suited for public websites: contact forms, read-only data APIs,
form submissions, and any backend logic that does not require user login.

For authenticated APIs (Cognito user accounts), use AuthorizedApiConstruct instead.
"""

from aws_cdk import (
    Duration,
    aws_lambda as lambda_,
    aws_lambda_nodejs as nodejs_lambda,
)
from constructs import Construct
from typing import Optional, Dict, List


class PublicApiConstruct(Construct):
    """
    Reusable L3 construct for a Lambda function exposed via Function URL (no auth).

    Uses Lambda Function URL instead of API Gateway — stays in the AWS always-free
    tier (1M requests/month forever) rather than the 12-month-only API Gateway tier.

    For Cognito-authenticated APIs, use AuthorizedApiConstruct instead.

    Example usage:
        api = PublicApiConstruct(
            self, "Api",
            entry="src/handlers/handler.js",
            environment={"TABLE_NAME": table.table_name}
        )

        web = WebAppConstruct(
            self, "Web",
            source_path="src/frontend/",
            config_data={"apiUrl": api.url}
        )

        # Grant the Lambda function access to your DynamoDB table
        table.grant_read_write_data(api.function)
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        entry: str,
        handler: str = "handler",
        environment: Optional[Dict[str, str]] = None,
        timeout: Duration = Duration.seconds(30),
        memory_size: int = 256,
        allowed_origins: Optional[List[str]] = None,
        **kwargs,
    ) -> None:
        """
        Initialize the PublicApi construct.

        Args:
            scope: CDK scope
            construct_id: Unique construct ID
            entry: Absolute path to the Lambda handler file (e.g. handler.js)
            handler: Exported function name in the handler file (default: "handler")
            environment: Environment variables passed to the Lambda function
            timeout: Lambda timeout (default: 30 seconds)
            memory_size: Lambda memory in MB (default: 256)
            allowed_origins: CORS allowed origins (default: ["*"])
            **kwargs: Additional arguments passed to Construct
        """
        super().__init__(scope, construct_id, **kwargs)

        self._function = nodejs_lambda.NodejsFunction(
            self,
            "Function",
            entry=entry,
            handler=handler,
            runtime=lambda_.Runtime.NODEJS_20_X,
            bundling=nodejs_lambda.BundlingOptions(
                force_docker_bundling=True,
                external_modules=["@aws-sdk/*"],
            ),
            environment=environment or {},
            timeout=timeout,
            memory_size=memory_size,
        )

        self._function_url = self._function.add_function_url(
            auth_type=lambda_.FunctionUrlAuthType.NONE,
            cors=lambda_.FunctionUrlCorsOptions(
                allowed_origins=allowed_origins or ["*"],
                allowed_methods=[lambda_.HttpMethod.ALL],
                allowed_headers=["Content-Type", "Authorization"],
                max_age=Duration.days(1),
            ),
        )

    @property
    def function(self) -> lambda_.Function:
        """The underlying Lambda function — use this to grant DynamoDB/S3 access"""
        return self._function

    @property
    def url(self) -> str:
        """The public HTTPS URL for this API"""
        return self._function_url.url

    @property
    def function_url(self) -> lambda_.FunctionUrl:
        """The Lambda Function URL resource"""
        return self._function_url
