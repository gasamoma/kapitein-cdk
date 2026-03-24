"""
Reusable CDK L3 Construct for API Gateway with Cognito Authorization
"""

from aws_cdk import (
    aws_apigateway as apigw,
    aws_cognito as cognito,
    aws_lambda as lambda_,
)
from constructs import Construct
from typing import List, Optional


class AuthorizedApiConstruct(Construct):
    """
    Reusable L3 construct for API Gateway with Cognito authorization.

    This construct bundles:
    - REST API Gateway with CORS
    - Cognito User Pools authorizer
    - Helper methods for adding authorized endpoints
    - Group-based authorization support

    Example usage:
        api = AuthorizedApiConstruct(
            self, "MyAPI",
            api_name="MyAPI",
            user_pool=cognito.user_pool,
            allowed_origins=["*"]
        )

        # Add authorized endpoint
        api.add_authorized_endpoint(
            path="/api/data",
            method="GET",
            lambda_function=my_lambda,
            required_groups=["Admins"]
        )
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        api_name: str,
        user_pool: cognito.UserPool,
        allowed_origins: Optional[List[str]] = None,
        deployment_stage: str = "prod",
        **kwargs
    ) -> None:
        """
        Initialize the Authorized API construct.

        Args:
            scope: CDK scope
            construct_id: Unique construct ID
            api_name: Name for the API Gateway
            user_pool: Cognito User Pool for authorization
            allowed_origins: CORS allowed origins (default: ["*"])
            deployment_stage: API Gateway deployment stage (default: "prod")
            **kwargs: Additional arguments passed to Construct
        """
        super().__init__(scope, construct_id, **kwargs)

        if allowed_origins is None:
            allowed_origins = ["*"]

        # Create REST API with CORS
        self._api = apigw.RestApi(
            self,
            "RestApi",
            rest_api_name=api_name,
            description=f"{api_name} REST API",
            deploy_options=apigw.StageOptions(
                stage_name=deployment_stage,
            ),
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=allowed_origins,
                allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                allow_headers=[
                    "Content-Type",
                    "X-Amz-Date",
                    "Authorization",
                    "X-Api-Key",
                    "X-Amz-Security-Token",
                ],
                allow_credentials=True,
            ),
        )

        # Create Cognito authorizer
        self._authorizer = apigw.CognitoUserPoolsAuthorizer(
            self,
            "Authorizer",
            cognito_user_pools=[user_pool]
        )

        # Store user pool for group-based auth
        self._user_pool = user_pool
        
        # Track created resources to avoid duplicates
        self._created_resources = {}

    def add_authorized_endpoint(
        self,
        path: str,
        method: str,
        lambda_function: lambda_.Function,
        required_groups: Optional[List[str]] = None,
        require_auth: bool = True,
    ) -> apigw.Method:
        """
        Add an authorized endpoint to the API.

        Args:
            path: API path (e.g., "/api/data")
            method: HTTP method (e.g., "GET", "POST")
            lambda_function: Lambda function to integrate
            required_groups: List of Cognito groups that should have access.
                **Note:** API Gateway only validates the JWT token — it does NOT
                enforce group membership. You must check the Cognito groups claim
                inside your Lambda handler:
                    groups = event["requestContext"]["authorizer"]["claims"]
                              .get("cognito:groups", "").split(",")
                    if "Admins" not in groups:
                        return {"statusCode": 403, "body": "Forbidden"}
            require_auth: Whether to require authentication (default: True)

        Returns:
            The created API Gateway Method
        """
        # Parse path and create resources
        path_parts = [p for p in path.split("/") if p]
        resource = self._api.root
        current_path = ""

        for part in path_parts:
            current_path = f"{current_path}/{part}"
            
            # Check if we've already created this resource
            if current_path in self._created_resources:
                resource = self._created_resources[current_path]
            else:
                # Create new resource and track it
                resource = resource.add_resource(part)
                self._created_resources[current_path] = resource

        # Create Lambda integration
        integration = apigw.LambdaIntegration(
            lambda_function,
            request_templates={"application/json": '{ "statusCode": "200" }'},
        )

        # Add method with optional authorization
        method_options = {}

        if require_auth:
            method_options["authorization_type"] = apigw.AuthorizationType.COGNITO
            method_options["authorizer"] = self._authorizer

            # Add group-based authorization if specified
            if required_groups:
                # Note: Group-based authorization is enforced at the Lambda level
                # by checking the Cognito groups claim in the authorizer context
                # The API Gateway authorizer only validates the JWT token
                pass

        method = resource.add_method(
            method,
            integration,
            **method_options
        )

        # Note: Lambda integration automatically grants invoke permission
        # No need to manually grant it here

        return method

    @property
    def api(self) -> apigw.RestApi:
        """The REST API Gateway"""
        return self._api

    @property
    def authorizer(self) -> apigw.CognitoUserPoolsAuthorizer:
        """The Cognito authorizer"""
        return self._authorizer

    @property
    def root_resource(self) -> apigw.Resource:
        """The root resource of the API"""
        return self._api.root

    @property
    def url(self) -> str:
        """The API Gateway URL"""
        return self._api.url
