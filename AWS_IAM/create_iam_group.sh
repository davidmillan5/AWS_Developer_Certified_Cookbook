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
