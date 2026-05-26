# Kapitein CDK

Reusable AWS CDK L3 constructs for common infrastructure patterns — and a complete automated deployment system for building websites with Claude Code.

---

## Reusable CDK constructs

Install in your own CDK project:

```bash
pip install git+https://github.com/gasamoma/kapitein-cdk.git@v0.1.0
```

Available constructs:

| Construct | Description |
|-----------|-------------|
| `WebAppConstruct` | S3 + CloudFront static web app hosting with OAC, SPA routing, config injection, optional build step |
| `PublicApiConstruct` | Lambda Function URL (no auth) — always-free tier; for public websites without user login |
| `CognitoWebPortalConstruct` | Cognito User Pool with groups, hosted UI domain, and web client |
| `AuthorizedApiConstruct` | API Gateway REST API with Cognito authorization and CORS — for authenticated apps |
| `S3VectorBucket` | S3 Vector bucket with index management |
| `S3VectorIndex` | Standalone vector index for existing S3 Vector buckets |

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
            source_path="src/frontend/",
            config_data={"apiEndpoint": api.url, "cognitoClientId": cognito.client_id},
        )
```

See [CONTRIBUTING.md](./CONTRIBUTING.md) for how to add new constructs.

---

## Website deployment system

A complete serverless website stack deployable by non-technical users — no AWS CLI, no local toolchain. Push code to GitHub, GitHub Actions deploys it.

**What it provisions:** CloudFront + S3 (frontend) · HTTP API Gateway + Lambda (backend) · DynamoDB (database)

**What users need:** An AWS account and a GitHub account. Nothing else.

[![Deploy OIDC Role to AWS](https://img.shields.io/badge/Step%201%3A%20Deploy%20to%20AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)](https://console.aws.amazon.com/cloudformation/home#/stacks/quickcreate?templateURL=https://raw.githubusercontent.com/gasamoma/kapitein-cdk/main/cloudformation/github-oidc-role.yaml&stackName=github-oidc-role)

> **Note for contributors:** The "Deploy to AWS" button points to the `main` branch and will only work after this PR is merged.

### Setup (4 steps, ~10 minutes)

**Step 1 — Create the AWS IAM role**

Click the button above. Fill in two fields:

| Field | What to enter |
|-------|--------------|
| **GitHubOrg** | Your GitHub username |
| **GitHubRepo** | Your repo name, or `*` for any repo |
| **CreateOidcProvider** | `Yes` (or `No` if GitHub OIDC already exists in your account — check IAM › Identity Providers) |

Click **Create stack**. When status shows `CREATE_COMPLETE`, copy the **RoleArn** from the Outputs tab.

**Step 2 — Fork this repository**

Click **Fork** at the top of this page.

**Step 3 — Add three repository variables**

In your fork: **Settings → Secrets and variables → Actions → Variables tab**

| Variable | Value |
|----------|-------|
| `AWS_ACCOUNT_ID` | Your 12-digit AWS account number |
| `AWS_REGION` | `us-east-1` (or your preferred region) |
| `AWS_ROLE_ARN` | The RoleArn from Step 1 |

**Step 4 — Push a change to deploy**

Edit `src/frontend/index.html`, commit, and push to `main`. The **Actions** tab shows progress. When finished, the CloudFront URL appears in the workflow summary.

First deployment: 5–10 minutes. Subsequent: 2–5 minutes.

---

### Building websites with Claude Code

Install [Claude Code](https://claude.ai/code), clone your fork, then use one of the agent templates in `templates/agents/` as your project `CLAUDE.md`:

| Template | Best for |
|----------|----------|
| [`CLAUDE_INTERVIEW.md`](./templates/CLAUDE_INTERVIEW.md) | Don't know where to start — Claude interviews you |
| [`agents/CLAUDE_ANIMATED_LANDING.md`](./templates/agents/CLAUDE_ANIMATED_LANDING.md) | Animated landing page with GSAP scroll effects |
| [`agents/CLAUDE_PORTFOLIO.md`](./templates/agents/CLAUDE_PORTFOLIO.md) | Portfolio or showcase site |
| [`agents/CLAUDE_BUSINESS_SITE.md`](./templates/agents/CLAUDE_BUSINESS_SITE.md) | Business site with contact form |
| [`agents/CLAUDE_VUE_SPA.md`](./templates/agents/CLAUDE_VUE_SPA.md) | Vue.js SPA (bundled via CDK Docker build) |

Copy your chosen template to the project root as `CLAUDE.md`, then start Claude Code in that folder.

For architecture reference (file conventions, API patterns, DynamoDB): [`templates/CLAUDE_ARCHITECTURE.md`](./templates/CLAUDE_ARCHITECTURE.md).

---

### When deployment fails

1. Click the **Actions** tab → click the failed run
2. The error and CloudFormation failure events are in the summary
3. Paste the error into Claude Code with: **"Help me fix this deployment error"**

---

### Visual preview with Claude Code

Claude Code can open a real browser and screenshot your live site. See [PLAYWRIGHT_SETUP.md](./PLAYWRIGHT_SETUP.md).

---

## License

Apache 2.0
