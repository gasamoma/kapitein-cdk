"""
Reusable CDK L3 Construct for S3 + CloudFront Web Hosting with OAC
"""

from aws_cdk import (
    RemovalPolicy,
    Duration,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_s3_deployment as s3deploy,
    aws_certificatemanager as acm,
    BundlingOptions,
    DockerImage,
)
from constructs import Construct
from typing import Optional, Dict


class WebAppConstruct(Construct):
    """
    Reusable L3 construct for S3 + CloudFront web hosting with modern OAC.

    This construct bundles:
    - S3 bucket with SSL enforcement and private access
    - CloudFront distribution with Origin Access Control (OAC) - modern approach
    - SPA routing support (403/404 → index.html)
    - Optional custom domain with ACM certificate
    - Config injection (API endpoints, Cognito client ID, etc.)
    - Optional build support for Vue.js/React apps

    Example usage:
        web_app = WebAppConstruct(
            self, "MyWebApp",
            source_path="src/web/",
            config_data={
                "apiEndpoint": api.url,
                "cognitoClientId": cognito.client_id
            },
            enable_spa_routing=True
        )

        # Access resources
        distribution_url = web_app.distribution.distribution_domain_name
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        source_path: Optional[str] = None,
        config_data: Optional[Dict] = None,
        enable_spa_routing: bool = True,
        custom_domain: Optional[str] = None,
        certificate_arn: Optional[str] = None,
        enable_build: bool = False,
        build_image: str = "node:22-alpine",
        removal_policy: RemovalPolicy = RemovalPolicy.RETAIN,
        **kwargs
    ) -> None:
        """
        Initialize the Web App construct.

        Args:
            scope: CDK scope
            construct_id: Unique construct ID
            source_path: Path to web app source files
            config_data: Dictionary to inject as config.json
            enable_spa_routing: Enable SPA routing (403/404 → index.html)
            custom_domain: Custom domain name (requires certificate_arn)
            certificate_arn: ARN of ACM certificate for custom domain
            enable_build: Enable Vue.js/React build during deployment
            build_image: Docker image for building (default: node:22-alpine)
            removal_policy: What to do on stack deletion (default: RETAIN)
            **kwargs: Additional arguments passed to Construct
        """
        super().__init__(scope, construct_id, **kwargs)

        # Create S3 bucket with strict security
        self._bucket = s3.Bucket(
            self,
            "WebsiteBucket",
            enforce_ssl=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=removal_policy,
            auto_delete_objects=(removal_policy == RemovalPolicy.DESTROY),
            encryption=s3.BucketEncryption.S3_MANAGED,
        )

        # Prepare CloudFront behavior options
        behavior_options = cloudfront.BehaviorOptions(
            origin=origins.S3BucketOrigin.with_origin_access_control(
                self._bucket
            ),
            viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD,
            cached_methods=cloudfront.CachedMethods.CACHE_GET_HEAD,
        )

        # Prepare CloudFront distribution options
        distribution_props = {
            "default_root_object": "index.html",
            "default_behavior": behavior_options,
            "minimum_protocol_version": cloudfront.SecurityPolicyProtocol.TLS_V1_2_2021,
        }

        # Add custom domain if provided
        if custom_domain and certificate_arn:
            certificate = acm.Certificate.from_certificate_arn(
                self,
                "Certificate",
                certificate_arn
            )
            distribution_props["domain_names"] = [custom_domain]
            distribution_props["certificate"] = certificate

        # Add SPA routing support if enabled
        if enable_spa_routing:
            distribution_props["error_responses"] = [
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.minutes(30),
                ),
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.minutes(30),
                ),
            ]

        # Create CloudFront distribution with OAC
        self._distribution = cloudfront.Distribution(
            self,
            "Distribution",
            **distribution_props
        )

        # Deploy source files if provided
        if source_path:
            sources = []

            # Add web app source (with optional build)
            if enable_build:
                # Build Vue.js/React app during deployment
                web_app_asset = s3deploy.Source.asset(
                    source_path,
                    bundling=BundlingOptions(
                        image=DockerImage.from_registry(build_image),
                        command=[
                            "sh", "-c",
                            """
                            set -e
                            echo "=== CDK Build Process ==="
                            cd /asset-input
                            echo "=== Installing Dependencies ==="
                            npm ci --include=dev --no-audit --no-fund
                            echo "=== Building Application ==="
                            npm run build
                            echo "=== Copying Output ==="
                            cp -r dist/* /asset-output/
                            echo "=== Build completed successfully ==="
                            """
                        ],
                        environment={
                            "NODE_ENV": "production",
                            "CI": "true",
                        },
                        working_directory="/asset-input",
                        user="root",
                    )
                )
                sources.append(web_app_asset)
            else:
                # Use source files as-is
                sources.append(s3deploy.Source.asset(source_path))

            # Add config.json if provided
            if config_data:
                config_asset = s3deploy.Source.json_data(
                    "config.json",
                    config_data
                )
                sources.append(config_asset)

            # Deploy to S3 with CloudFront cache invalidation
            s3deploy.BucketDeployment(
                self,
                "DeployWebsite",
                sources=sources,
                destination_bucket=self._bucket,
                distribution=self._distribution,
                distribution_paths=["/*"],
            )

    @property
    def bucket(self) -> s3.Bucket:
        """The S3 bucket hosting the web app"""
        return self._bucket

    @property
    def distribution(self) -> cloudfront.Distribution:
        """The CloudFront distribution"""
        return self._distribution

    @property
    def domain_name(self) -> str:
        """The CloudFront distribution domain name"""
        return self._distribution.distribution_domain_name

    @property
    def distribution_id(self) -> str:
        """The CloudFront distribution ID"""
        return self._distribution.distribution_id

    @property
    def url(self) -> str:
        """The full HTTPS URL to the web app"""
        return f"https://{self.domain_name}"
