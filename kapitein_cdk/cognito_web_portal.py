"""
Reusable CDK L3 Construct for Cognito User Pool with Groups
"""

from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_cognito as cognito,
)
from constructs import Construct
from typing import List, Optional, Dict


class CognitoWebPortalConstruct(Construct):
    """
    Reusable L3 construct for creating a Cognito User Pool with user groups.

    This construct bundles:
    - Cognito User Pool with email-based sign-in
    - User Pool Client for web applications
    - Cognito Domain for hosted UI
    - Multiple user groups for role-based access control

    Example usage:
        cognito = CognitoWebPortalConstruct(
            self, "MyCognito",
            user_pool_name="MyAppUserPool",
            groups=["Admins", "Users", "Viewers"],
            self_signup_enabled=False
        )

        # Access resources
        user_pool = cognito.user_pool
        client_id = cognito.client.user_pool_client_id
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        user_pool_name: str,
        groups: List[str],
        self_signup_enabled: bool = False,
        domain_prefix: Optional[str] = None,
        invite_email_subject: Optional[str] = None,
        invite_email_body: Optional[str] = None,
        removal_policy: RemovalPolicy = RemovalPolicy.RETAIN,
        **kwargs
    ) -> None:
        """
        Initialize the Cognito Web Portal construct.

        Args:
            scope: CDK scope
            construct_id: Unique construct ID
            user_pool_name: Name for the Cognito User Pool
            groups: List of group names to create
            self_signup_enabled: Allow users to self-register (default: False)
            domain_prefix: Custom domain prefix (auto-generated if None)
            invite_email_subject: Custom invitation email subject (default: generic)
            invite_email_body: Custom invitation email HTML body. Use {username} and {####} placeholders.
            removal_policy: What to do on stack deletion (default: RETAIN for safety)
            **kwargs: Additional arguments passed to Construct
        """
        super().__init__(scope, construct_id, **kwargs)

        if invite_email_subject is None:
            invite_email_subject = f"Welcome to {user_pool_name} - Your account has been created"
        if invite_email_body is None:
            invite_email_body = (
                f"<h2>Welcome to {user_pool_name}!</h2>"
                "<p>An account has been created for you.</p>"
                "<p><strong>Username:</strong> {username}<br>"
                "<strong>Temporary Password:</strong> {####}</p>"
                "<p>You will be asked to change your password on first login.</p>"
            )

        # Create User Pool with email-based sign-in
        self._user_pool = cognito.UserPool(
            self,
            "UserPool",
            user_pool_name=user_pool_name,
            self_sign_up_enabled=self_signup_enabled,
            removal_policy=removal_policy,
            # Email as primary sign-in
            sign_in_aliases=cognito.SignInAliases(
                email=True,
                phone=False,
                username=False
            ),
            # Standard attributes
            standard_attributes=cognito.StandardAttributes(
                email=cognito.StandardAttribute(
                    required=True,
                    mutable=True
                )
            ),
            # Email verification
            user_verification=cognito.UserVerificationConfig(
                email_subject="Verify your email for your application",
                email_body="Thanks for signing up! Your verification code is {####}",
                email_style=cognito.VerificationEmailStyle.CODE,
            ),
            # Invitation email
            user_invitation=cognito.UserInvitationConfig(
                email_subject=invite_email_subject,
                email_body=invite_email_body,
                sms_message="Your username is {username} and temporary password is {####}",
            ),
            # Password policy
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_symbols=False,
            ),
            # Account recovery
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
        )

        # Create User Pool Client for web applications
        self._client = self._user_pool.add_client(
            "WebClient",
            user_pool_client_name=f"{user_pool_name}WebClient",
            generate_secret=False,  # Public client (SPA)
            auth_flows=cognito.AuthFlow(
                user_password=True,
                user_srp=True,
            ),
            # OAuth settings for hosted UI
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(
                    authorization_code_grant=True,
                    implicit_code_grant=True,
                ),
                scopes=[
                    cognito.OAuthScope.EMAIL,
                    cognito.OAuthScope.OPENID,
                    cognito.OAuthScope.PROFILE,
                ],
            ),
        )

        # Create Cognito Domain with unique prefix
        if domain_prefix is None:
            # Auto-generate unique domain prefix
            import re
            import hashlib

            stack_name = Stack.of(self).stack_name.lower()
            # Replace underscores and non-alphanumeric chars with hyphens
            stack_clean = re.sub(r'[^a-z0-9-]', '-', stack_name)
            pool_clean = re.sub(r'[^a-z0-9-]', '-', user_pool_name.lower())

            # Create a hash for uniqueness (includes account ID)
            account_id = Stack.of(self).account
            hash_input = f"{stack_name}-{user_pool_name}-{account_id}".encode()
            hash_suffix = hashlib.md5(hash_input).hexdigest()[:8]

            # Build domain prefix: pool-stack-hash
            domain_prefix = f"{pool_clean}-{stack_clean}-{hash_suffix}"
            # Ensure length < 63 characters and remove consecutive/trailing hyphens
            domain_prefix = re.sub(r'-+', '-', domain_prefix[:63].strip("-"))

        self._domain = self._user_pool.add_domain(
            "Domain",
            cognito_domain=cognito.CognitoDomainOptions(
                domain_prefix=domain_prefix
            )
        )

        # Create user groups for role-based access control
        self._groups: Dict[str, cognito.CfnUserPoolGroup] = {}
        for group_name in groups:
            group = cognito.CfnUserPoolGroup(
                self,
                f"Group{group_name}",
                user_pool_id=self._user_pool.user_pool_id,
                group_name=group_name,
                description=f"{group_name} user group",
            )
            self._groups[group_name] = group

    @property
    def user_pool(self) -> cognito.UserPool:
        """The Cognito User Pool"""
        return self._user_pool

    @property
    def client(self) -> cognito.UserPoolClient:
        """The User Pool Client for web applications"""
        return self._client

    @property
    def domain(self) -> cognito.UserPoolDomain:
        """The Cognito Domain for hosted UI"""
        return self._domain

    @property
    def groups(self) -> Dict[str, cognito.CfnUserPoolGroup]:
        """Dictionary of user groups (group_name -> CfnUserPoolGroup)"""
        return self._groups

    @property
    def user_pool_id(self) -> str:
        """The User Pool ID"""
        return self._user_pool.user_pool_id

    @property
    def user_pool_arn(self) -> str:
        """The User Pool ARN"""
        return self._user_pool.user_pool_arn

    @property
    def client_id(self) -> str:
        """The User Pool Client ID"""
        return self._client.user_pool_client_id
