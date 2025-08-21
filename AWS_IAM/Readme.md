# IAM Commands

## Creating a Security Group Using Python SDK

```python
### Creating a Security group

### First execute the command pip install boto3 and pip install python-dotenv

import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Load environment variables from .env file
load_dotenv()


def create_iam_group_explicit(group_name, path='/'):
    """
    Create an IAM group using explicit credentials from .env
    """
    try:
        # Get credentials from environment variables
        access_key = os.getenv('AWS_ACCESS_KEY_ID')
        secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        region = os.getenv('AWS_DEFAULT_REGION', 'us-east-2')

        # Validate that we have the required credentials
        if not access_key or not secret_key:
            raise ValueError("AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY must be set in .env file")

        # Create IAM client with explicit credentials
        iam = boto3.client(
            'iam',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )

        # Create the group
        response = iam.create_group(
            GroupName=group_name,
            Path=path
        )

        print(f"✓ Group '{group_name}' created successfully")
        print(f"Group ARN: {response['Group']['Arn']}")
        return response

    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'EntityAlreadyExists':
            print(f"Group '{group_name}' already exists")
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


# Usage
if __name__ == "__main__":
    create_iam_group_explicit('DevelopersGroup')



```



## Script command through .sh file


```.sh
#!/bin/bash

# -------------------------------------------
# Script: create_iam_group.sh
# Purpose: Create a new IAM group in AWS
# Requirements:
#   - AWS CLI installed
#   - A .env file located ONE LEVEL ABOVE this script
# -------------------------------------------

# Define path to the .env file (one directory above this script)
ENV_FILE="../.env"

# STEP 1: Load environment variables from .env file
if [ -f "$ENV_FILE" ]; then
  echo "Loading AWS credentials from $ENV_FILE..."

  # Read non-comment lines and export them as environment variables
  export $(grep -v '^#' "$ENV_FILE" | xargs)
else
  echo "❌ Error: .env file not found at $ENV_FILE"
  echo "Make sure your .env file with AWS credentials is one level above this script."
  exit 1
fi

# STEP 2: Set IAM group name
GROUP_NAME="Developers"

echo "🔧 Creating IAM group named: $GROUP_NAME ..."
aws iam create-group --group-name "$GROUP_NAME" --profile david_admin

# STEP 3: Done
echo "✅ Done! IAM group '$GROUP_NAME' has been created (if it didn't already exist)."


```

### Command Line

```bash
aws iam create-group --group-name DevOpsGroup --region us-east-2 --profile david_admin

```




## Creating users

### Command Line

```bash

aws iam create-user --user-name Eren_DevOps --region us-east-2 --profile david_admin

```