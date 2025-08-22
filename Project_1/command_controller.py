import boto3
from botocore.exceptions import ClientError


def createNewUser():
    print("Do you want to create a new user: ")
    response = input().lower()
    if response == "yes":
        print(" Please enter the name of the new User: ")
        newUser = input().title()
        print("Enter your AWS Access Key Id: ")
        awsAccessKeyId = input()
        print("Enter your AWS Secret Access Key Id: ")
        awsSecretAccessKey = input()
        print("Choose The region where the new User will be created: ")
        awsRegion = input()
        print("Enter your AWS Profile: ")
        awsProfile = input()
        if not awsAccessKeyId or not awsSecretAccessKey:
            print("❌ Error: Please make sure AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY are in your .env file")
            return

    # Connect to AWS
    iam = boto3.client(
        'iam',
        aws_access_key_id=awsAccessKeyId,
        aws_secret_access_key=awsSecretAccessKey,
        region_name=awsRegion
    )

    # Create the user
    response = iam.create_user(UserName=newUser)

    # Success message
    print(f"✅ Success! User '{newUser}' has been created!")
    print(f"📋 User details:")
    print(f"   - Name: {response['User']['UserName']}")
    print(f"   - ID: {response['User']['UserId']}")
    print(f"   - Created: {response['User']['CreateDate']}")

    # except ClientError as error:
    # # Handle different types of errors
    # error_code = error.response['Error']['Code']
    #
    # if error_code == 'EntityAlreadyExists':
    #     print(f"❌ Error: User '{newUser}' already exists!")
    # elif error_code == 'InvalidClientTokenId':
    #     print("❌ Error: Your AWS credentials are invalid. Check your .env file.")
    # elif error_code == 'AccessDenied':
    #     print("❌ Error: You don't have permission to create users.")
    # else:
    #     print(f"❌ Error: Something went wrong - {error}")

createNewUser()
