import boto3
import json
from botocore.exceptions import ClientError


def aim_operation_console():
    print("Welcome To The Console From AIM Service in AWS what do you want to do Today? Select:"
          "\n1. To Create a New User \n2. To Create a New Group \n3. To Create a New Role")
    response = int(input())
    if response == 1:
        new_user = input("Please enter the name of the new User: ").title()
        access_key_id = input("Enter your AWS Access Key Id: ")
        secret_access_key = input("Enter your AWS Secret Access Key Id: ")
        aws_region = input("Choose The region where the new User will be created: ")

        if not access_key_id or not secret_access_key:
            print("❌ Error: Please make sure AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are inserted")
            return None

        try:
            # Connect to AWS
            iam = boto3.client(
                'iam',
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
                region_name=aws_region
            )

            # Create the user
            response = iam.create_user(UserName=new_user)

            # Success message
            print(f"✅ Success! User '{new_user}' has been created!")
            print(f"📋 User details:")
            print(f"   - Name: {response['User']['UserName']}")
            print(f"   - ID: {response['User']['UserId']}")
            print(f"   - Created: {response['User']['CreateDate']}")

        except ClientError as error:
            # Handle different types of errors
            error_code = error.response['Error']['Code']

            if error_code == 'EntityAlreadyExists':
                print(f"❌ Error: User '{new_user}' already exists!")
            elif error_code == 'InvalidClientTokenId':
                print("❌ Error: Your AWS credentials are invalid. Check your .env file.")
            elif error_code == 'AccessDenied':
                print("❌ Error: You don't have permission to create users.")
            else:
                print(f"❌ Error: Something went wrong - {error}")
    elif response == 2:
        print("Please enter the name of the new Group: ")
        new_group = input()
        print("Enter your AWS Access Key Id: ")
        access_key_id = input()
        print("Enter your AWS Secret Access Key Id: ")
        secret_access_key = input()
        print("Choose The region where the new User will be created: ")
        aws_region = input()

        if not access_key_id or not secret_access_key:
            print("❌ Error: Please make sure AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are inserted")
            return None

        try:
            # Connect to AWS
            iam = boto3.client(
                'iam',
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
                region_name=aws_region
            )

            response = iam.create_group(
                GroupName=new_group
            )

            print(f"✓ Group '{new_group}' created successfully")
            print(f"Group ARN: {response['Group']['Arn']}")
            return response

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'EntityAlreadyExists':
                print(f"Group '{new_group}' already exists")
            elif error_code == 'InvalidClientTokenId':
                print(f"Invalid credentials. Check your AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
            elif error_code == 'AccessDenied':
                print(f"Access denied. Check your IAM permissions")
            else:
                print(f"Error creating group: {e}")
            return None
        except ValueError as e:
            print(f"Configuration error: {e}")
            return None
    elif response == 3:
        new_role = input("Please enter the name of the new Role: ")
        access_key_id = input("Enter your AWS Access Key Id: ")
        secret_access_key = input("Enter your AWS Secret Access Key Id: ")
        aws_region = input("Choose The region where the new Role will be created: ")
        service_principal = input("Insert service prinicipal")

        # Define trust policy
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": service_principal
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        if not access_key_id or not secret_access_key:
            print("❌ Error: Please make sure AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are inserted")
            return None

        try:
            # Connect to AWS
            iam = boto3.client(
                'iam',
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
                region_name=aws_region
            )

            # Create role parameters
            params = {
                'RoleName': new_role,
                'AssumeRolePolicyDocument': json.dumps(trust_policy)
            }

            # Create the role
            response = iam.create_role(**params)

            print(f"✅ Role '{new_role}' created successfully!")
            print(f"ARN: {response['Role']['Arn']}")

            return response

        except ClientError as e:
            print(f"❌ Error creating role: {e}")
            return None

    return None


if __name__ == "__main__":
    aim_operation_console()
