# Kapitein CDK

Reusable AWS CDK L3 constructs for common infrastructure patterns.

## Installation

```bash
pip install git+https://github.com/gasamoma/kapitein-cdk.git@v0.1.0
```

## Available Constructs

| Construct | Description |
|-----------|-------------|
| `CognitoWebPortalConstruct` | Cognito User Pool with groups, hosted UI domain, and web client |
| `AuthorizedApiConstruct` | API Gateway with Cognito authorization and CORS |
| `WebAppConstruct` | S3 + CloudFront static web app hosting with OAC |
| `S3VectorBucket` | S3 Vector bucket with index management |
| `S3VectorIndex` | Standalone vector index for existing buckets |

## Usage

```python
from kapitein_cdk import CognitoWebPortalConstruct, AuthorizedApiConstruct, WebAppConstruct

class MyStack(Stack):
    def __init__(self, scope, id, **kwargs):
        super().__init__(scope, id, **kwargs)

        cognito = CognitoWebPortalConstruct(
            self, "Auth",
            user_pool_name="MyApp",
            groups=["Admins", "Users"],
            self_signup_enabled=False,
        )

        api = AuthorizedApiConstruct(
            self, "API",
            api_name="MyAPI",
            user_pool=cognito.user_pool,
        )

        web = WebAppConstruct(
            self, "Web",
            source_path="src/web/",
            config_data={"apiEndpoint": api.url},
        )
```

## Versioning

```bash
pip install git+https://github.com/gasamoma/kapitein-cdk.git@v0.1.0
```

## License

Apache 2.0
