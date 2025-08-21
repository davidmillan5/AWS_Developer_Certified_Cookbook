import boto3
import os
import json
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Load environment variables from .env file
load_dotenv()


def create_iam_role(role_name, trust_policy, description=None, path='/'):
    """
    Create an IAM role with a trust policy

    Args:
        role_name (str): Name of the role to create
        trust_policy (dict): Trust policy document
        description (str): Optional description for the role
        path (str): Path for the role (default: '/')
    """
    try:
        # Get credentials from environment variables
        access_key = os.getenv('AWS_ACCESS_KEY_ID')
        secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')

        # Validate credentials
        if not access_key or not secret_key:
            raise ValueError("AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY must be set in .env file")

        # Create IAM client
        iam = boto3.client(
            'iam',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )

        # Prepare parameters
        params = {
            'RoleName': role_name,
            'AssumeRolePolicyDocument': json.dumps(trust_policy),
            'Path': path
        }

        if description:
            params['Description'] = description

        # Create the role
        response = iam.create_role(**params)

        print(f"✅ Role '{role_name}' created successfully!")
        print(f"📋 Role Details:")
        print(f"   - Name: {response['Role']['RoleName']}")
        print(f"   - ARN: {response['Role']['Arn']}")
        print(f"   - Created: {response['Role']['CreateDate']}")

        return response

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'EntityAlreadyExists':
            print(f"❌ Role '{role_name}' already exists")
        elif error_code == 'InvalidClientTokenId':
            print("❌ Invalid credentials. Check your .env file")
        elif error_code == 'AccessDenied':
            print("❌ Access denied. Check your IAM permissions")
        else:
            print(f"❌ Error creating role: {e}")
        return None
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        return None


def create_ec2_role(role_name, description="Role for EC2 instances"):
    """
    Create a role that can be assumed by EC2 instances
    """
    # Trust policy for EC2
    ec2_trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "ec2.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }

    return create_iam_role(role_name, ec2_trust_policy, description)


def create_lambda_role(role_name, description="Role for Lambda functions"):
    """
    Create a role that can be assumed by Lambda functions
    """
    # Trust policy for Lambda
    lambda_trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }

    return create_iam_role(role_name, lambda_trust_policy, description)


def create_cross_account_role(role_name, trusted_account_id, description="Cross-account access role"):
    """
    Create a role that can be assumed by another AWS account

    Args:
        role_name (str): Name of the role
        trusted_account_id (str): AWS account ID that can assume this role
        description (str): Role description
    """
    # Trust policy for cross-account access
    cross_account_trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "AWS": f"arn:aws:iam::{trusted_account_id}:root"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }

    return create_iam_role(role_name, cross_account_trust_policy, description)


def attach_policy_to_role(role_name, policy_arn):
    """
    Attach a managed policy to a role

    Args:
        role_name (str): Name of the role
        policy_arn (str): ARN of the policy to attach
    """
    try:
        # Get credentials
        access_key = os.getenv('AWS_ACCESS_KEY_ID')
        secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')

        # Create IAM client
        iam = boto3.client(
            'iam',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )

        # Attach policy
        iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy_arn
        )

        print(f"✅ Policy '{policy_arn}' attached to role '{role_name}'")

    except ClientError as e:
        print(f"❌ Error attaching policy: {e}")


def create_role_with_policies(role_name, trust_policy, policy_arns=None, inline_policies=None):
    """
    Create a role and attach policies to it

    Args:
        role_name (str): Name of the role
        trust_policy (dict): Trust policy document
        policy_arns (list): List of managed policy ARNs to attach
        inline_policies (dict): Dictionary of inline policies {policy_name: policy_document}
    """
    try:
        # Create the role first
        role_response = create_iam_role(role_name, trust_policy)
        if not role_response:
            return None

        # Get IAM client
        access_key = os.getenv('AWS_ACCESS_KEY_ID')
        secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')

        iam = boto3.client(
            'iam',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )

        # Attach managed policies
        if policy_arns:
            for policy_arn in policy_arns:
                try:
                    iam.attach_role_policy(
                        RoleName=role_name,
                        PolicyArn=policy_arn
                    )
                    print(f"✅ Attached managed policy: {policy_arn}")
                except ClientError as e:
                    print(f"❌ Failed to attach policy {policy_arn}: {e}")

        # Create inline policies
        if inline_policies:
            for policy_name, policy_document in inline_policies.items():
                try:
                    iam.put_role_policy(
                        RoleName=role_name,
                        PolicyName=policy_name,
                        PolicyDocument=json.dumps(policy_document)
                    )
                    print(f"✅ Created inline policy: {policy_name}")
                except ClientError as e:
                    print(f"❌ Failed to create inline policy {policy_name}: {e}")

        return role_response

    except Exception as e:
        print(f"❌ Error creating role with policies: {e}")
        return None


def list_roles():
    """List all IAM roles"""
    try:
        # Get credentials
        access_key = os.getenv('AWS_ACCESS_KEY_ID')
        secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')

        # Create IAM client
        iam = boto3.client(
            'iam',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )

        # List roles
        response = iam.list_roles()
        roles = response['Roles']

        if roles:
            print(f"\n📋 Found {len(roles)} roles:")
            for role in roles:
                print(f"   - {role['RoleName']} (Created: {role['CreateDate']})")
        else:
            print("No roles found")

        return roles

    except ClientError as e:
        print(f"❌ Error listing roles: {e}")
        return []


def verify_credentials():
    """Verify AWS credentials"""
    try:
        access_key = os.getenv('AWS_ACCESS_KEY_ID')
        secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        region = os.getenv('AWS_DEFAULT_REGION', 'us-east-1')

        if not access_key or not secret_key:
            print("❌ AWS credentials not found in .env file")
            return False

        # Create STS client
        sts = boto3.client(
            'sts',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )

        identity = sts.get_caller_identity()
        print(f"✅ Connected as: {identity.get('Arn')}")
        return True

    except ClientError as e:
        print(f"❌ Credential verification failed: {e}")
        return False


# Usage examples
if __name__ == "__main__":
    print("🚀 AWS IAM Role Creator")
    print("=" * 40)

    # Verify credentials
    if not verify_credentials():
        print("Please check your .env file")
        exit(1)

    print("\n" + "=" * 40)

    # Example 1: Create EC2 role
    print("Example 1: Creating EC2 role...")
    create_ec2_role('MyEC2Role', 'Role for EC2 instances to access S3')

    print("\n" + "-" * 40)

    # Example 2: Create Lambda role
    print("Example 2: Creating Lambda role...")
    create_lambda_role('MyLambdaRole', 'Role for Lambda functions')

    print("\n" + "-" * 40)

    # Example 3: Create role with policies
    print("Example 3: Creating role with policies...")

    # Define trust policy for EC2
    ec2_trust = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "ec2.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }
        ]
    }

    # Managed policies to attach
    managed_policies = [
        'arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess',
        'arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy'
    ]

    # Inline policy
    inline_policy = {
        'CustomS3Policy': {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject",
                        "s3:PutObject"
                    ],
                    "Resource": "arn:aws:s3:::my-bucket/*"
                }
            ]
        }
    }

    create_role_with_policies(
        'MyCustomRole',
        ec2_trust,
        policy_arns=managed_policies,
        inline_policies=inline_policy
    )

    print("\n" + "-" * 40)

    # List all roles
    print("Current roles:")
    list_roles()