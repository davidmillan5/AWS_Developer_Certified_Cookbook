#!/bin/bash

# -------------------------------------------
# AWS User Creation Script
# Creates a new IAM user using environment variables
# -------------------------------------------

# Define path to the .env file (adjust as needed)
ENV_FILE="../.env"

# Load environment variables from .env file if it exists
if [ -f "$ENV_FILE" ]; then
    echo "📄 Loading environment variables from $ENV_FILE ..."
    export $(grep -v '^#' "$ENV_FILE" | xargs)
else
    echo "⚠️  No .env file found at $ENV_FILE. Using system environment variables."
fi

# Use AWS_DEFAULT_REGION from env or default to us-east-2
AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:-us-east-2}

# User name to create (you can update this or make it a parameter)
USER_NAME="testuser123"

echo "🚀 AWS User Creator Script"
echo "=========================="
echo "Region: $AWS_DEFAULT_REGION"
echo "User to create: $USER_NAME"
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ Error: AWS CLI is not installed."
    echo "Please install it first: https://aws.amazon.com/cli/"
    exit 1
fi

# Check if AWS credentials are configured
echo "🔐 Checking AWS credentials..."
if aws sts get-caller-identity &> /dev/null; then
    echo "✅ AWS credentials are valid"
    aws sts get-caller-identity --query 'Arn' --output text
    echo ""
else
    echo "❌ Error: AWS credentials are not configured or invalid."
    echo "Please check your .env file or run 'aws configure'"
    exit 1
fi

# Create the user
echo "👤 Creating user '$USER_NAME'..."

# Try creating the user and capture error if any
error_output=$(aws iam create-user --user-name "$USER_NAME" --region "$AWS_DEFAULT_REGION" 2>&1)
exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo "✅ Success! User '$USER_NAME' has been created!"
    echo ""
    echo "📋 User Details:"
    aws iam get-user --user-name "$USER_NAME" --query 'User.[UserName,UserId,CreateDate,Arn]' --output table
else
    if [[ "$error_output" == *"EntityAlreadyExists"* ]]; then
        echo "❌ Error: User '$USER_NAME' already exists!"
    elif [[ "$error_output" == *"InvalidClientTokenId"* ]]; then
        echo "❌ Error: Your AWS credentials are invalid."
    elif [[ "$error_output" == *"AccessDenied"* ]]; then
        echo "❌ Error: You don't have permission to create users."
    else
        echo "❌ Error: Something went wrong:"
        echo "$error_output"
    fi
    exit $exit_code
fi

echo ""
echo "🎉 Done! User creation completed."
