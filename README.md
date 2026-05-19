# Kapitein CDK

**Build and deploy a real website on AWS — no coding experience required.**

You write the content with Claude Code. This repo handles the AWS infrastructure.
Every deployment runs automatically in the cloud — no AWS CLI, no terminal commands, no local setup beyond what you already have.

[![Deploy OIDC Role to AWS](https://img.shields.io/badge/Step%201%3A%20Deploy%20to%20AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)](https://console.aws.amazon.com/cloudformation/home#/stacks/quickcreate?templateURL=https://raw.githubusercontent.com/gasamoma/kapitein-cdk/main/cloudformation/github-oidc-role.yaml&stackName=github-oidc-role)

> **Note for contributors:** The "Deploy to AWS" button points to the `main` branch. It will work after this PR is merged.

---

## What you get

- A website hosted on AWS CloudFront — globally fast, HTTPS, always on
- A backend API (AWS Lambda) for contact forms, data, anything interactive
- A database (DynamoDB) if your site needs to store information
- Fully automated deployments — push to GitHub, site updates in minutes
- No monthly server costs for low-traffic sites (AWS free tier covers it)

---

## What you need

1. **AWS account** — free at [aws.amazon.com](https://aws.amazon.com) (no credit card required for free tier)
2. **GitHub account** — free at [github.com](https://github.com)

That's it. You do not need the AWS CLI, Node.js, Python, or any developer tools installed locally.

---

## Setup (4 steps, ~10 minutes total)

### Step 1 — Create the AWS IAM role

Click the button above (or [click here](https://console.aws.amazon.com/cloudformation/home#/stacks/quickcreate?templateURL=https://raw.githubusercontent.com/gasamoma/kapitein-cdk/main/cloudformation/github-oidc-role.yaml&stackName=github-oidc-role)).

You'll see a CloudFormation form. Fill in two fields:

| Field | What to enter |
|-------|--------------|
| **GitHubOrg** | Your GitHub username (the name in your profile URL) |
| **GitHubRepo** | Your repository name, or `*` to allow any repo |

Scroll down, check the acknowledgement box, and click **Create stack**.

Wait 2–3 minutes. When the status shows `CREATE_COMPLETE`, click the **Outputs** tab and copy the **RoleArn** value — you'll need it in Step 3.

---

### Step 2 — Fork this repository

Click **Fork** at the top of this GitHub page. This creates your own copy of the repo where you'll add your website.

---

### Step 3 — Add three variables to GitHub

In your forked repo, go to **Settings → Secrets and variables → Actions → Variables tab** and add:

| Variable name | Value |
|--------------|-------|
| `AWS_ACCOUNT_ID` | Your 12-digit AWS account number (found in the top-right corner of the AWS console) |
| `AWS_REGION` | `us-east-1` (or your preferred region) |
| `AWS_ROLE_ARN` | The RoleArn you copied in Step 1 |

---

### Step 4 — Push a change to deploy

Edit `src/frontend/index.html` in your forked repo (click the pencil icon on GitHub, change anything, click Commit).

GitHub Actions will automatically run. Click the **Actions** tab to watch it. When it finishes, the URL to your live site appears in the workflow summary.

**First deployment takes 5–10 minutes.** Subsequent ones take 2–5 minutes.

---

## Building your website with Claude Code

Install [Claude Code](https://claude.ai/code) on your computer, then:

1. Clone your forked repo: `git clone https://github.com/YOUR-USERNAME/kapitein-cdk`
2. Open that folder in Claude Code
3. Copy `templates/CLAUDE_INTERVIEW.md` into the folder as `CLAUDE.md`
4. Type: **Start a new project**

Claude will interview you about your site, then build it. When you're happy, push to GitHub and it deploys automatically.

For architecture context (how the backend and database work), see `templates/CLAUDE_ARCHITECTURE.md`.

---

## When deployment fails

1. Click the **Actions** tab in your GitHub repo
2. Click the failed run
3. The error and CloudFormation failure events are shown in the summary
4. Copy the error and paste it into Claude Code with: **"Help me fix this deployment error"**

Claude will diagnose and fix it.

---

## Preview your site visually with Claude Code

Claude Code can open a real browser, screenshot your live site, and compare it to a design reference.

See [PLAYWRIGHT_SETUP.md](./PLAYWRIGHT_SETUP.md) for the 3-step setup.

---

## For developers — reusable CDK constructs

This repo is also a Python CDK library. Install it in your own CDK projects:

```bash
pip install git+https://github.com/gasamoma/kapitein-cdk.git@v0.1.0
```

Available constructs:

| Construct | Description |
|-----------|-------------|
| `WebAppConstruct` | S3 + CloudFront static web app hosting with OAC |
| `CognitoWebPortalConstruct` | Cognito User Pool with groups, hosted UI, and web client |
| `AuthorizedApiConstruct` | API Gateway with Cognito authorization and CORS |
| `S3VectorBucket` | S3 Vector bucket with index management |
| `S3VectorIndex` | Standalone vector index for existing buckets |

```python
from kapitein_cdk import WebAppConstruct, CognitoWebPortalConstruct, AuthorizedApiConstruct

class MyStack(Stack):
    def __init__(self, scope, id, **kwargs):
        super().__init__(scope, id, **kwargs)

        web = WebAppConstruct(
            self, "Web",
            source_path="src/frontend/",
            config_data={"apiEndpoint": api.url},
        )
```

See [CONTRIBUTING.md](./CONTRIBUTING.md) for how to add new constructs.

---

## License

Apache 2.0
