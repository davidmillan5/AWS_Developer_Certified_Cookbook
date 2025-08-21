import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Load environment variables from .env file
load_dotenv()


def create_aws_user(user_name):
    """
    Create a new AWS IAM user

    Args:
        user_name (str): Name of the user you want to create
    """
    try:
        # Get your AWS credentials from the .env file
        access_key = os.getenv('AWS_ACCESS_KEY_ID')
        secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        region = os.getenv('AWS_DEFAULT_REGION', 'us-east-2')

        # Check if we have the credentials
        if not access_key or not secret_key:
            print("❌ Error: Please make sure AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are in your .env file")
            return

        # Connect to AWS
        iam = boto3.client(
            'iam',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )

        # Create the user
        response = iam.create_user(UserName=user_name)

        # Success message
        print(f"✅ Success! User '{user_name}' has been created!")
        print(f"📋 User details:")
        print(f"   - Name: {response['User']['UserName']}")
        print(f"   - ID: {response['User']['UserId']}")
        print(f"   - Created: {response['User']['CreateDate']}")

    except ClientError as error:
        # Handle different types of errors
        error_code = error.response['Error']['Code']

        if error_code == 'EntityAlreadyExists':
            print(f"❌ Error: User '{user_name}' already exists!")
        elif error_code == 'InvalidClientTokenId':
            print("❌ Error: Your AWS credentials are invalid. Check your .env file.")
        elif error_code == 'AccessDenied':
            print("❌ Error: You don't have permission to create users.")
        else:
            print(f"❌ Error: Something went wrong - {error}")


# Main program
if __name__ == "__main__":
    print("🚀 AWS User Creator")
    print("==================")

    # The name of the user you want to create
    new_user_name = "David_Developer"  # Change this to whatever name you want

    # Create the user
    create_aws_user(new_user_name)